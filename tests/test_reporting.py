from pathlib import Path

import pandas as pd

from hybrid_query_construction.io import append_jsonl
from hybrid_query_construction.reporting import build_report


def _row(dataset: str, method: str, ndcg: float, depth: int) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "protocol_version": "hqc-formal-v1",
        "dataset": dataset,
        "query_id": "q1",
        "draw_id": 0,
        "track": "controlled",
        "method": method,
        "reference_count": 5,
        "rrf_constant": 60,
        "ndcg_at_10": ndcg,
        "recall_at_20": ndcg,
        "dense_depth": depth,
        "sparse_depth": depth,
        "sparse_support": 20,
        "sparse_exhausted": False,
        "ordered_top20": [f"d{index}" for index in range(20)],
        "generation_artifact_sha256": "a" * 64,
        "dense_ranking_sha256": "b" * 64,
        "sparse_ranking_sha256": "c" * 64,
        "method_config_sha256": "d" * 64,
        "replay_trace_sha256": "e" * 64,
        "fallback": False,
    }


def test_report_keeps_development_out_of_confirmatory_tables(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    rows = []
    for dataset in ("fiqa", "arguana", "webis-touche2020", "scidocs", "scifact"):
        rows.extend(
            [
                _row(dataset, "original", 0.4, 100),
                _row(dataset, "bridge_shared", 0.45, 90),
                _row(dataset, "proposed", 0.5, 80),
            ]
        )
    append_jsonl(raw / "results.jsonl", rows)
    output = tmp_path / "report"
    build_report(raw, output)

    main = pd.read_csv(output / "main-results.csv")
    development = pd.read_csv(output / "development-results.csv")
    tests = pd.read_csv(output / "primary-paired-tests.csv")
    access_intervals = pd.read_csv(output / "access-macro-bootstrap.csv")
    classifications = pd.read_csv(output / "outcome-classification.csv")
    assert set(main["dataset"]) == {"fiqa", "arguana", "webis-touche2020", "scidocs"}
    assert set(development["dataset"]) == {"scifact"}
    assert len(tests) == 8
    assert set(access_intervals["dataset"]) == {"macro_equal_dataset"}
    assert set(access_intervals["metric"]) == {
        "dense_total_reduction_pct",
        "sparse_total_reduction_pct",
        "dual_depth_improvement_rate",
    }
    assert set(classifications["comparison"]) == {
        "proposed_vs_original",
        "proposed_vs_bridge_shared",
    }
    assert set(classifications["classification"]) <= {"强阳性", "混合", "负面"}
