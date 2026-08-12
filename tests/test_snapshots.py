import json
from pathlib import Path

from hybrid_query_construction.datasets import prepare_nested_snapshots


def test_snapshots_are_nested_and_retain_relevant(tmp_path: Path) -> None:
    source = tmp_path / "data" / "processed" / "toy"
    source.mkdir(parents=True)
    with (source / "corpus.jsonl").open("w") as handle:
        for index in range(8):
            handle.write(json.dumps({"_id": f"d{index}", "text": str(index)}) + "\n")
    (source / "queries.jsonl").write_text('{"_id":"q","text":"x"}\n')
    (source / "qrels.tsv").write_text("query-id\tcorpus-id\tscore\nq\td0\t1\nq\td1\t2\n")
    manifests = prepare_nested_snapshots("toy", tmp_path, [4, 6, 8])
    assert [row["actual_size"] for row in manifests] == [4, 6, 8]
    previous: set[str] = set()
    for size in (4, 6, 8):
        rows = [
            json.loads(line)
            for line in (source.parent / f"toy-{size}" / "corpus.jsonl")
            .read_text()
            .splitlines()
        ]
        identifiers = {row["_id"] for row in rows}
        assert {"d0", "d1"} <= identifiers
        assert previous <= identifiers
        previous = identifiers
