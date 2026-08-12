import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from hybrid_query_construction.generation import parse_references, run_generation
from hybrid_query_construction.models import DecodingConfig, GenerationAttempt


def test_parse_exact_reference_object() -> None:
    raw = '{"references":["one","two","three","four","five"]}'
    assert parse_references(raw, 5) == ("one", "two", "three", "four", "five")


def test_parse_allows_whole_response_fence_only() -> None:
    raw = '```json\n{"references":["one"]}\n```'
    assert parse_references(raw, 1) == ("one",)


@pytest.mark.parametrize(
    "raw",
    [
        '{"references":["one","one"]}',
        '{"references":["one"],"extra":1}',
        '{"references":[]}',
        "not json",
    ],
)
def test_parse_rejects_invalid_outputs(raw: str) -> None:
    with pytest.raises((ValueError, __import__("json").JSONDecodeError)):
        parse_references(raw, 2)


def test_generation_attempt_requires_valid_index() -> None:
    with pytest.raises(ValidationError):
        GenerationAttempt(
            attempt_index=2,
            raw_text="bad",
            finish_reason="length",
            prompt_tokens=1,
            completion_tokens=1,
            parse_error="invalid",
        )


def test_successful_retry_is_recorded_as_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeGenerator:
        def __init__(self, model_directory: Path) -> None:
            self.manifest = {
                "model_id": "test/model",
                "source_revision": "abc",
                "dtype": "bfloat16",
                "artifact_sha256": "artifact",
            }
            self.calls = 0

        def generate_batch(
            self,
            system_prompt: str,
            requests: list[tuple[str, str, int, str | None]],
            seed: int,
            decoding: DecodingConfig,
        ) -> list[tuple[str, int, int, str]]:
            self.calls += 1
            if self.calls == 1:
                return [("not json", 3, 2, "schema_stop") for _ in requests]
            return [('{"references":["fixed"]}', 5, 4, "schema_stop") for _ in requests]

    root = tmp_path
    (root / "uv.lock").write_text("lock", encoding="utf-8")
    prompt = root / "prompt.txt"
    prompt.write_text("prompt", encoding="utf-8")
    output = root / "records.jsonl"
    monkeypatch.setattr("hybrid_query_construction.generation.MLXGenerator", FakeGenerator)
    monkeypatch.setattr("hybrid_query_construction.generation.current_commit", lambda _: "c0")
    monkeypatch.setattr(
        "hybrid_query_construction.generation.importlib.metadata.version",
        lambda _: "0.31.2",
    )
    run_generation(
        root=root,
        dataset="tiny",
        queries={"q1": "query"},
        output_path=output,
        prompt_path=prompt,
        model_config={
            "model_id": "test/model",
            "revision": "abc",
            "tokenizer_revision": "abc",
            "dtype": "bfloat16",
            "backend": "mlx_lm",
            "backend_version": "0.31.2",
            "local_model_path": "model",
            "query_batch_size": 8,
            "draws": 1,
            "reference_count": 1,
            "decoding": {
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 20,
                "repetition_penalty": 1.0,
                "max_new_tokens": 32,
                "stop_sequence": "}",
            },
        },
        protocol_version="test-v1",
        prompt_name="test",
    )
    record = json.loads(output.read_text(encoding="utf-8"))
    assert record["status"] == "ok"
    assert record["parsed_references"] == ["fixed"]
    assert record["retry_count"] == 1
    assert len(record["attempts"]) == 2
