import pytest
from pydantic import ValidationError

from hybrid_query_construction.generation import parse_references
from hybrid_query_construction.models import GenerationAttempt


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
