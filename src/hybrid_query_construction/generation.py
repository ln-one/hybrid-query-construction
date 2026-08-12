from __future__ import annotations

import importlib.metadata
import json
import subprocess
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .io import append_jsonl, canonical_json, read_jsonl, sha256_file, stable_seed
from .model_conversion import verify_model_artifact
from .models import DecodingConfig, GenerationAttempt, GenerationRecord


def parse_references(raw_text: str, expected_count: int) -> tuple[str, ...]:
    text = raw_text.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    value = json.loads(text)
    if not isinstance(value, dict) or set(value) != {"references"}:
        raise ValueError("expected one object containing only 'references'")
    references = value["references"]
    if not isinstance(references, list) or len(references) != expected_count:
        raise ValueError(f"expected exactly {expected_count} references")
    if not all(isinstance(reference, str) and reference.strip() for reference in references):
        raise ValueError("all references must be non-empty strings")
    normalized = [
        unicodedata.normalize("NFC", reference).strip().casefold() for reference in references
    ]
    if len(set(normalized)) != expected_count:
        raise ValueError("references must be distinct after normalization")
    return tuple(unicodedata.normalize("NFC", reference).strip() for reference in references)


def current_commit(root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


class MLXGenerator:
    def __init__(self, model_directory: Path) -> None:
        from mlx_lm import load

        self.model_directory = model_directory
        self.manifest = verify_model_artifact(model_directory)
        self.model, self.tokenizer = load(str(model_directory))

    def _prompt_tokens(
        self,
        system_prompt: str,
        query_id: str,
        query: str,
        previous_invalid_output: str | None = None,
    ) -> list[int]:
        user_content = canonical_json({"query_id": query_id, "query": query})
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        if previous_invalid_output is not None:
            messages.extend(
                [
                    {"role": "assistant", "content": previous_invalid_output},
                    {
                        "role": "user",
                        "content": (
                            "The previous output failed strict JSON validation. Return only "
                            "the requested JSON object with the exact reference count."
                        ),
                    },
                ]
            )
        return self.tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True
        )

    def generate_batch(
        self,
        system_prompt: str,
        requests: list[tuple[str, str, int, str | None]],
        seed: int,
        decoding: DecodingConfig,
    ) -> list[tuple[str, int, int, str]]:
        import mlx.core as mx
        from mlx_lm.generate import BatchGenerator
        from mlx_lm.sample_utils import make_sampler

        if not requests:
            return []
        if not decoding.do_sample:
            raise ValueError("formal MLX generation expects stochastic sampling")
        if decoding.repetition_penalty != 1.0:
            raise ValueError("formal MLX generation supports repetition_penalty=1.0")
        prompts = [
            self._prompt_tokens(system_prompt, query_id, query, invalid)
            for query_id, query, _, invalid in requests
        ]
        mx.random.seed(seed)
        schema_stop = self.tokenizer.encode(decoding.stop_sequence)
        generator = BatchGenerator(
            self.model,
            stop_tokens=[
                *[[token] for token in self.tokenizer.eos_token_ids],
                schema_stop,
            ],
            sampler=make_sampler(
                temp=decoding.temperature,
                top_p=decoding.top_p,
                top_k=decoding.top_k,
            ),
        )
        uids = generator.insert(prompts, [decoding.max_new_tokens] * len(prompts))
        generated = {uid: [] for uid in uids}
        finishes: dict[int, str] = {}
        try:
            while responses := generator.next_generated():
                for response in responses:
                    if response.finish_reason == "stop":
                        matched = (
                            list(response.match_sequence)
                            if response.match_sequence is not None
                            else []
                        )
                        if matched == schema_stop:
                            generated[response.uid].extend(schema_stop)
                        finishes[response.uid] = "schema_stop"
                    else:
                        generated[response.uid].append(int(response.token))
                        if response.finish_reason is not None:
                            finishes[response.uid] = response.finish_reason
        finally:
            generator.close()
        results = []
        for uid, prompt_tokens in zip(uids, prompts, strict=True):
            tokens = generated[uid]
            results.append(
                (
                    self.tokenizer.decode(tokens),
                    len(prompt_tokens),
                    len(tokens),
                    finishes[uid],
                )
            )
        return results


def run_generation(
    *,
    root: Path,
    dataset: str,
    queries: dict[str, str],
    output_path: Path,
    prompt_path: Path,
    model_config: dict[str, Any],
    protocol_version: str,
    prompt_name: str,
    reference_count: int | None = None,
    draws: int | None = None,
) -> None:
    existing = (
        {(row["query_id"], int(row["draw_id"])) for row in read_jsonl(output_path)}
        if output_path.exists()
        else set()
    )
    prompt = prompt_path.read_text(encoding="utf-8")
    prompt_hash = sha256_file(prompt_path)
    decoding = DecodingConfig.model_validate(model_config["decoding"])
    if model_config["backend"] != "mlx_lm":
        raise ValueError(f"unsupported formal generation backend: {model_config['backend']}")
    backend_version = importlib.metadata.version("mlx-lm")
    if backend_version != model_config["backend_version"]:
        raise RuntimeError(
            f"mlx-lm version mismatch: {backend_version} != {model_config['backend_version']}"
        )
    generator = MLXGenerator(root / model_config["local_model_path"])
    expected_model = (
        model_config["model_id"],
        model_config["revision"],
        model_config["dtype"],
    )
    actual_model = (
        generator.manifest["model_id"],
        generator.manifest["source_revision"],
        generator.manifest["dtype"],
    )
    if actual_model != expected_model:
        raise RuntimeError(f"converted model does not match generator config: {actual_model}")
    model_artifact_sha256 = generator.manifest["artifact_sha256"]
    runtime_hash = sha256_file(root / "uv.lock")
    commit = current_commit(root)
    expected_count = int(reference_count or model_config["reference_count"])
    draw_count = int(draws or model_config["draws"])
    query_ids = sorted(queries)
    batch_size = int(model_config["query_batch_size"])
    for batch_start in range(0, len(query_ids), batch_size):
        batch_ids = query_ids[batch_start : batch_start + batch_size]
        missing_pairs = [
            (query_id, draw_id)
            for query_id in batch_ids
            for draw_id in range(draw_count)
            if (query_id, draw_id) not in existing
        ]
        if not missing_pairs:
            continue
        seed = stable_seed(
            protocol_version,
            dataset,
            prompt_hash,
            str(batch_start // batch_size),
        )
        all_requests = [
            (query_id, queries[query_id], draw_id, None)
            for query_id in batch_ids
            for draw_id in range(draw_count)
        ]
        initial_outputs = generator.generate_batch(prompt, all_requests, seed, decoding)
        output_by_pair = {
            (query_id, draw_id): output
            for (query_id, _, draw_id, _), output in zip(
                all_requests, initial_outputs, strict=True
            )
        }
        states: dict[tuple[str, int], dict[str, Any]] = {}
        retry_requests: list[tuple[str, str, int, str | None]] = []
        for query_id, draw_id in missing_pairs:
            raw, prompt_tokens, completion_tokens, finish_reason = output_by_pair[
                (query_id, draw_id)
            ]
            state: dict[str, Any] = {
                "raw": raw,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "finish_reason": finish_reason,
                "references": (),
                "status": "generation_failed",
                "attempts": [],
            }
            try:
                state["references"] = parse_references(raw, expected_count)
                state["status"] = "ok"
                parse_error = None
            except (ValueError, json.JSONDecodeError) as error:
                parse_error = f"{type(error).__name__}: {error}"
                retry_requests.append((query_id, queries[query_id], draw_id, raw))
            state["attempts"].append(
                GenerationAttempt(
                    attempt_index=0,
                    raw_text=raw,
                    finish_reason=finish_reason,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    parse_error=parse_error,
                )
            )
            states[(query_id, draw_id)] = state

        if retry_requests:
            retry_outputs = generator.generate_batch(prompt, retry_requests, seed, decoding)
            for request, output in zip(retry_requests, retry_outputs, strict=True):
                query_id, _, draw_id, _ = request
                raw, prompt_tokens, completion_tokens, finish_reason = output
                state = states[(query_id, draw_id)]
                state.update(
                    raw=raw,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    finish_reason=finish_reason,
                )
                try:
                    state["references"] = parse_references(raw, expected_count)
                    state["status"] = "ok"
                    parse_error = None
                except (ValueError, json.JSONDecodeError) as error:
                    state["status"] = "generation_failed"
                    parse_error = f"{type(error).__name__}: {error}"
                state["attempts"].append(
                    GenerationAttempt(
                        attempt_index=1,
                        raw_text=raw,
                        finish_reason=finish_reason,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        parse_error=parse_error,
                    )
                )

        for query_id, draw_id in missing_pairs:
            state = states[(query_id, draw_id)]
            record = GenerationRecord(
                protocol_version=protocol_version,
                dataset=dataset,
                query_id=query_id,
                query_text=queries[query_id],
                draw_id=draw_id,
                prompt_path=str(prompt_path.relative_to(root)),
                prompt_sha256=prompt_hash,
                model_id=model_config["model_id"],
                model_revision=model_config["revision"],
                tokenizer_revision=model_config["tokenizer_revision"],
                backend=model_config["backend"],
                backend_version=backend_version,
                model_artifact_sha256=model_artifact_sha256,
                seed=seed,
                decoding=decoding,
                raw_text=state["raw"],
                parsed_references=state["references"],
                finish_reason=state["finish_reason"],
                prompt_tokens=state["prompt_tokens"],
                completion_tokens=state["completion_tokens"],
                retry_count=len(state["attempts"]) - 1,
                attempts=tuple(state["attempts"]),
                status=state["status"],
                runtime_lock_sha256=runtime_hash,
                code_commit=commit,
                created_at_utc=datetime.now(UTC),
            )
            append_jsonl(output_path, [record.model_dump(mode="json")])
