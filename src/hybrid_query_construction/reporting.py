from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .io import atomic_write_text, read_jsonl

PRIMARY_METRICS = ("ndcg_at_10", "recall_at_20", "dense_depth", "sparse_depth")


def load_result_rows(input_directory: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(input_directory.rglob("*.jsonl")):
        rows.extend(read_jsonl(path))
    return rows


def build_report(input_directory: Path, output_directory: Path) -> Path:
    rows = load_result_rows(input_directory)
    if not rows:
        raise RuntimeError("no real per-query result records found")
    output_directory.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    aggregates = (
        frame.groupby(["dataset", "method"], as_index=False)[list(PRIMARY_METRICS)]
        .mean()
        .sort_values(["dataset", "method"])
    )
    aggregate_path = output_directory / "main-results.csv"
    aggregates.to_csv(aggregate_path, index=False)

    lines = [
        "# 正式实验结果报告",
        "",
        "> 本报告只读取真实的逐查询记录，不接受 mock 或手工填写的结果。",
        "",
        "## 数据完整性",
        "",
        f"- 逐查询记录：{len(frame):,} 条",
        f"- 数据集：{frame['dataset'].nunique()} 个",
        f"- 方法：{frame['method'].nunique()} 个",
        "",
        "## 主结果",
        "",
        aggregates.to_markdown(index=False),
        "",
        "## 结论边界",
        "",
        "逻辑访问深度不等同于在线延迟；生成成本、表示构造、检索执行和融合回放分别核算。",
    ]
    report_path = output_directory / "REPORT.md"
    atomic_write_text(report_path, "\n".join(lines) + "\n")
    return report_path
