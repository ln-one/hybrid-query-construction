import subprocess
from pathlib import Path

from hybrid_query_construction.audit import (
    CONTROLLED_CHANNELS,
    _expected_ranking_keys,
    _is_ancestor,
)


def test_expected_ranking_keys_cover_all_registered_cells() -> None:
    keys = _expected_ranking_keys({"q1", "q2"}, {"q1"}, include_fidelity=True)
    assert len(keys) == 2 * 2 + 1 * 3 * 3 * len(CONTROLLED_CHANNELS) + 2 * 3 * 3 * 2
    assert ("q1", 2, "controlled", "sparse_anchor", 5) in keys
    assert ("q2", 2, "fidelity", "dense_hyde", 8) in keys
    assert ("q2", 0, "base", "dense_original", 0) in keys


def test_generation_commit_may_precede_current_head() -> None:
    root = Path(__file__).resolve().parents[1]
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    parent = subprocess.check_output(
        ["git", "rev-parse", "HEAD^"], cwd=root, text=True
    ).strip()
    assert _is_ancestor(root, parent, head)
