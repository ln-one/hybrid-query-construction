from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DecodingConfig(StrictModel):
    do_sample: bool
    temperature: float
    top_p: float
    top_k: int
    repetition_penalty: float
    max_new_tokens: int
    stop_sequence: str


class GenerationAttempt(StrictModel):
    attempt_index: int = Field(ge=0, le=1)
    raw_text: str
    finish_reason: str
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    parse_error: str | None


class GenerationRecord(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    protocol_version: str
    dataset: str
    query_id: str
    query_text: str
    draw_id: int = Field(ge=0)
    prompt_path: str
    prompt_sha256: str
    model_id: str
    model_revision: str
    tokenizer_revision: str
    backend: str
    backend_version: str
    structured_output_backend: str
    structured_output_backend_version: str
    model_artifact_sha256: str
    seed: int = Field(ge=0)
    decoding: DecodingConfig
    raw_text: str
    parsed_references: tuple[str, ...]
    finish_reason: str
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    retry_count: int = Field(ge=0, le=1)
    attempts: tuple[GenerationAttempt, ...]
    status: Literal["ok", "generation_failed"]
    runtime_lock_sha256: str
    code_commit: str
    created_at_utc: datetime

    @field_validator("attempts")
    @classmethod
    def validate_attempts(
        cls, attempts: tuple[GenerationAttempt, ...]
    ) -> tuple[GenerationAttempt, ...]:
        if not 1 <= len(attempts) <= 2:
            raise ValueError("one or two generation attempts are required")
        if tuple(attempt.attempt_index for attempt in attempts) != tuple(range(len(attempts))):
            raise ValueError("generation attempt indices must be consecutive")
        return attempts

    @field_validator("parsed_references")
    @classmethod
    def validate_references(cls, references: tuple[str, ...]) -> tuple[str, ...]:
        normalized = [reference.strip().casefold() for reference in references]
        if any(not reference for reference in normalized):
            raise ValueError("references must be non-empty")
        if len(set(normalized)) != len(normalized):
            raise ValueError("references must be distinct")
        return references


class QueryResult(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    protocol_version: str
    dataset: str
    query_id: str
    draw_id: int
    track: Literal["controlled", "fidelity", "ablation", "robustness", "scale", "tiny"]
    method: str
    reference_count: int = Field(ge=0)
    rrf_constant: int = Field(gt=0)
    ndcg_at_10: float = Field(ge=0.0, le=1.0)
    recall_at_20: float = Field(ge=0.0, le=1.0)
    dense_depth: int = Field(ge=0)
    sparse_depth: int = Field(ge=0)
    sparse_support: int = Field(ge=0)
    sparse_exhausted: bool
    ordered_top20: tuple[str, ...]
    generation_artifact_sha256: str
    dense_ranking_sha256: str
    sparse_ranking_sha256: str
    method_config_sha256: str
    replay_trace_sha256: str
    fallback: bool


class ReplayResult(StrictModel):
    ordered_top_k: tuple[str, ...]
    dense_depth: int
    sparse_depth: int
    sparse_exhausted: bool
    checks: int
    trace: tuple[tuple[int, int, str], ...]
