from __future__ import annotations

import json
import subprocess
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .io import append_jsonl, canonical_json, read_jsonl, sha256_file, stable_seed
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


class LocalGenerator:
    def __init__(self, model_id: str, revision: str, device: str, dtype: str) -> None:
        self.model_id = model_id
        self.revision = revision
        self.device = device
        torch_dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16}[dtype]
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            revision=revision,
            dtype=torch_dtype,
            low_cpu_mem_usage=True,
        ).to(device)
        self.model.eval()

    @torch.inference_mode()
    def generate(
        self,
        system_prompt: str,
        query_id: str,
        query: str,
        seed: int,
        decoding: DecodingConfig,
        previous_invalid_output: str | None = None,
    ) -> tuple[str, int, int, str]:
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
        rendered = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(rendered, return_tensors="pt").to(self.device)
        torch.manual_seed(seed)
        if self.device == "mps":
            torch.mps.manual_seed(seed)
        output = self.model.generate(
            **inputs,
            do_sample=decoding.do_sample,
            temperature=decoding.temperature,
            top_p=decoding.top_p,
            top_k=decoding.top_k,
            repetition_penalty=decoding.repetition_penalty,
            max_new_tokens=decoding.max_new_tokens,
            pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        completion = output[0, inputs["input_ids"].shape[1] :]
        raw = self.tokenizer.decode(completion, skip_special_tokens=True)
        finish = (
            "eos"
            if completion.numel() and int(completion[-1]) == self.tokenizer.eos_token_id
            else "length"
        )
        return raw, int(inputs["input_ids"].shape[1]), int(completion.shape[0]), finish


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
    generator = LocalGenerator(
        model_config["model_id"],
        model_config["revision"],
        model_config["device"],
        model_config["dtype"],
    )
    runtime_hash = sha256_file(root / "uv.lock")
    commit = current_commit(root)
    expected_count = int(reference_count or model_config["reference_count"])
    draw_count = int(draws or model_config["draws"])
    for query_id in sorted(queries):
        for draw_id in range(draw_count):
            if (query_id, draw_id) in existing:
                continue
            seed = stable_seed(protocol_version, dataset, query_id, str(draw_id), prompt_hash)
            raw = ""
            references: tuple[str, ...] = ()
            prompt_tokens = completion_tokens = 0
            finish_reason = "failed"
            status = "generation_failed"
            retry_count = 0
            attempts: list[GenerationAttempt] = []
            for attempt in range(2):
                retry_count = attempt
                raw, prompt_tokens, completion_tokens, finish_reason = generator.generate(
                    prompt,
                    query_id,
                    queries[query_id],
                    seed,
                    decoding,
                    previous_invalid_output=raw if attempt else None,
                )
                try:
                    references = parse_references(raw, expected_count)
                except (ValueError, json.JSONDecodeError) as error:
                    attempts.append(
                        GenerationAttempt(
                            attempt_index=attempt,
                            raw_text=raw,
                            finish_reason=finish_reason,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            parse_error=f"{type(error).__name__}: {error}",
                        )
                    )
                    continue
                attempts.append(
                    GenerationAttempt(
                        attempt_index=attempt,
                        raw_text=raw,
                        finish_reason=finish_reason,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        parse_error=None,
                    )
                )
                status = "ok"
                break
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
                seed=seed,
                decoding=decoding,
                raw_text=raw,
                parsed_references=references,
                finish_reason=finish_reason,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                retry_count=retry_count,
                attempts=tuple(attempts),
                status=status,
                runtime_lock_sha256=runtime_hash,
                code_commit=commit,
                created_at_utc=datetime.now(UTC),
            )
            append_jsonl(output_path, [record.model_dump(mode="json")])
