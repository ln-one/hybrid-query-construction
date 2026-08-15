from pathlib import Path

import pandas as pd

from hybrid_query_construction.io import append_jsonl
from hybrid_query_construction.reporting import build_report


def _row(
    dataset: str,
    method: str,
    ndcg: float,
    depth: int,
    *,
    track: str = "controlled",
    condition_id: str = "primary",
) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "protocol_version": "hqc-formal-v1",
        "dataset": dataset,
        "query_id": "q1",
        "draw_id": 0,
        "track": track,
        "condition_id": condition_id,
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
    method_intervals = pd.read_csv(output / "main-macro-bootstrap.csv")
    classifications = pd.read_csv(output / "outcome-classification.csv")
    report = (output / "REPORT.md").read_text(encoding="utf-8")
    assert set(main["dataset"]) == {"fiqa", "arguana", "webis-touche2020", "scidocs"}
    assert set(development["dataset"]) == {"scifact"}
    assert len(tests) == 8
    assert set(access_intervals["dataset"]) == {"macro_equal_dataset"}
    assert set(access_intervals["metric"]) == {
        "dense_total_reduction_pct",
        "sparse_total_reduction_pct",
        "dual_depth_improvement_rate",
    }
    assert set(method_intervals["metric"]) == {
        "ndcg_at_10",
        "recall_at_20",
        "dense_depth",
        "sparse_depth",
    }
    assert set(classifications["comparison"]) == {
        "proposed_vs_original",
        "proposed_vs_bridge_shared",
    }
    assert set(classifications["classification"]) <= {"强阳性", "混合", "负面"}
    for heading in (
        "## Held-out 各数据集主结果",
        "## 2×2 机制实验（数据集等权）",
        "## 公开方法完整复现",
        "## 消融与敏感性",
        "## 鲁棒性：第二生成模型与第二 Dense 编码器",
        "## 规模趋势",
        "## 开发集机制检查（不用于 held-out 主结论）",
    ):
        assert heading in report


def test_report_separates_conditions_and_holm_families(tmp_path: Path, monkeypatch) -> None:
    raw = tmp_path / "raw"
    rows = []
    for dataset in ("fiqa", "arguana", "webis-touche2020", "scidocs"):
        rows.extend(
            [
                _row(dataset, "original", 0.4, 100),
                _row(dataset, "bridge_shared", 0.45, 90),
                _row(dataset, "proposed", 0.5, 80),
                _row(
                    dataset,
                    "proposed",
                    0.6,
                    70,
                    track="robustness",
                    condition_id="mistral",
                ),
                _row(
                    dataset,
                    "proposed",
                    0.7,
                    60,
                    track="robustness",
                    condition_id="contriever",
                ),
            ]
        )
    append_jsonl(raw / "results.jsonl", rows)
    pvalues = iter((0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08))
    monkeypatch.setattr(
        "hybrid_query_construction.reporting.stratified_sign_flip_pvalue",
        lambda differences: next(pvalues),
    )

    output = tmp_path / "report"
    build_report(raw, output)

    robustness = pd.read_csv(output / "robustness-results.csv")
    tests = pd.read_csv(output / "primary-paired-tests.csv")
    assert set(robustness["condition_id"]) == {"mistral", "contriever"}
    first_family = tests[tests["comparison"] == "proposed_vs_original"]
    second_family = tests[tests["comparison"] == "proposed_vs_bridge_shared"]
    assert first_family["p_holm"].max() == 0.06
    assert second_family["p_holm"].min() == 0.2
