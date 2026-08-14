from pathlib import Path

from hybrid_query_construction.tiny import run_tiny


def test_tiny_pipeline(tmp_path: Path) -> None:
    result = run_tiny(tmp_path / "tiny.json")
    assert result["ordered_top20"] == result["replay"]["ordered_top_k"]
    assert result["reuse"]["itemwise_equal"]
    assert result["reuse"]["ranking_sha256_equal"]
    assert result["reuse"]["fusion_cache_hit"]
    assert result["reuse"]["fusion_cache_top20_equal"]
    assert 0.0 <= result["ndcg_at_10"] <= 1.0
    assert 0.0 <= result["recall_at_20"] <= 1.0
