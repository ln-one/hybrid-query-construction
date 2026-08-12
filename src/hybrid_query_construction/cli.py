from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from .datasets import (
    load_queries,
    prepare_beir_dataset,
    prepare_nested_snapshots,
    unseal_qrels,
)
from .environment import capture_environment
from .evaluate import evaluate_rankings
from .generation import run_generation
from .locking import create_preheldout_lock
from .reporting import build_report
from .runner import build_rankings
from .tiny import run_tiny
from .verification import verify_repository


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def command_tiny(args: argparse.Namespace) -> None:
    print(json.dumps(run_tiny(Path(args.output)), ensure_ascii=False, indent=2))


def command_prepare(args: argparse.Namespace) -> None:
    root = repository_root()
    config = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    selected = [*config["development"], *config["heldout"]]
    for dataset in selected:
        if args.dataset and dataset["id"] != args.dataset:
            continue
        heldout = dataset in config["heldout"]
        url = f"{config['base_url']}/{dataset['archive']}"
        manifest = prepare_beir_dataset(
            dataset["id"], url, root, heldout=heldout, split=dataset["split"]
        )
        print(json.dumps(manifest, ensure_ascii=False))


def command_generate(args: argparse.Namespace) -> None:
    root = repository_root()
    config = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))
    model = config[args.model]
    queries = load_queries(root / "data" / "processed" / args.dataset / "queries.jsonl")
    if args.hash_limit:
        from .io import hash_selected

        selected = hash_selected(queries, args.hash_limit)
        queries = {key: queries[key] for key in selected}
    elif args.limit:
        queries = {key: queries[key] for key in sorted(queries)[: args.limit]}
    prompt_path = root / args.prompt
    run_generation(
        root=root,
        dataset=args.dataset,
        queries=queries,
        output_path=root / args.output,
        prompt_path=prompt_path,
        model_config=model,
        protocol_version="hqc-formal-v1",
        prompt_name=prompt_path.stem,
        reference_count=args.reference_count,
        draws=args.draws,
    )


def command_rank(args: argparse.Namespace) -> None:
    root = repository_root()
    config = yaml.safe_load((root / args.config).read_text(encoding="utf-8"))

    def optional_path(value: str | None) -> Path | None:
        return root / value if value else None

    print(
        build_rankings(
            root=root,
            dataset=args.dataset,
            retriever_config=config,
            bridge_generation=optional_path(args.bridge_generation),
            mugi_generation=optional_path(args.mugi_generation),
            hyde_generation=optional_path(args.hyde_generation),
            query2doc_generation=optional_path(args.query2doc_generation),
            query_limit=args.limit,
            reference_counts=tuple(args.reference_counts),
            dense_key=args.dense_key,
            run_id=args.run_id,
        )
    )


def command_evaluate(args: argparse.Namespace) -> None:
    root = repository_root()
    results = evaluate_rankings(
        root=root,
        dataset=args.dataset,
        store_path=root / args.store,
        output_directory=root / args.output,
        reference_count=args.reference_count,
        constant=args.rrf_constant,
        result_track=args.result_track,
        include_fidelity=not args.skip_fidelity,
        output_id=args.output_id,
    )
    print("\n".join(str(path) for path in results))


def command_snapshots(args: argparse.Namespace) -> None:
    root = repository_root()
    for manifest in prepare_nested_snapshots(args.dataset, root, args.sizes):
        print(json.dumps(manifest, ensure_ascii=False))


def command_environment(args: argparse.Namespace) -> None:
    root = repository_root()
    print(
        json.dumps(capture_environment(root, root / args.output), ensure_ascii=False, indent=2)
    )


def command_lock(args: argparse.Namespace) -> None:
    root = repository_root()
    print(json.dumps(create_preheldout_lock(root, root / args.output), indent=2))


def command_unseal(args: argparse.Namespace) -> None:
    root = repository_root()
    print(unseal_qrels(args.dataset, root, root / args.lock))


def command_report(args: argparse.Namespace) -> None:
    root = repository_root()
    print(build_report(root / args.input, root / args.output, root=root))


def command_verify(args: argparse.Namespace) -> None:
    print(json.dumps(verify_repository(Path(args.root).resolve()), indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hqc")
    subparsers = parser.add_subparsers(required=True)
    tiny = subparsers.add_parser("tiny")
    tiny.add_argument("--output", required=True)
    tiny.set_defaults(function=command_tiny)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--config", default="configs/datasets/formal-v1.yaml")
    prepare.add_argument("--dataset")
    prepare.set_defaults(function=command_prepare)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--config", default="configs/generators/formal-v1.yaml")
    generate.add_argument("--model", choices=("primary", "robustness"), default="primary")
    generate.add_argument("--dataset", required=True)
    generate.add_argument("--prompt", default="prompts/primary-reference-v1.txt")
    generate.add_argument("--output", required=True)
    generate.add_argument("--limit", type=int)
    generate.add_argument("--hash-limit", type=int)
    generate.add_argument("--reference-count", type=int)
    generate.add_argument("--draws", type=int)
    generate.set_defaults(function=command_generate)

    rank = subparsers.add_parser("rank")
    rank.add_argument("--config", default="configs/retrievers/formal-v1.yaml")
    rank.add_argument("--dataset", required=True)
    rank.add_argument("--bridge-generation")
    rank.add_argument("--mugi-generation")
    rank.add_argument("--hyde-generation")
    rank.add_argument("--query2doc-generation")
    rank.add_argument("--reference-counts", type=int, nargs="+", default=(1, 3, 5))
    rank.add_argument("--limit", type=int)
    rank.add_argument("--dense-key", default="dense")
    rank.add_argument("--run-id", default="primary")
    rank.set_defaults(function=command_rank)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--dataset", required=True)
    evaluate.add_argument("--store", required=True)
    evaluate.add_argument("--output", default="artifacts/results/raw")
    evaluate.add_argument("--reference-count", type=int, default=5)
    evaluate.add_argument("--rrf-constant", type=int, default=60)
    evaluate.add_argument(
        "--result-track", choices=("controlled", "ablation", "robustness", "scale")
    )
    evaluate.add_argument("--skip-fidelity", action="store_true")
    evaluate.add_argument("--output-id")
    evaluate.set_defaults(function=command_evaluate)

    snapshots = subparsers.add_parser("snapshots")
    snapshots.add_argument("--dataset", default="trec-covid")
    snapshots.add_argument("--sizes", type=int, nargs="+", required=True)
    snapshots.set_defaults(function=command_snapshots)

    environment = subparsers.add_parser("environment")
    environment.add_argument("--output", default="artifacts/lock/environment.json")
    environment.set_defaults(function=command_environment)

    lock = subparsers.add_parser("lock")
    lock.add_argument("--output", default="artifacts/lock/pre-heldout-v1.json")
    lock.set_defaults(function=command_lock)

    unseal = subparsers.add_parser("unseal")
    unseal.add_argument("--dataset", required=True)
    unseal.add_argument("--lock", default="artifacts/lock/pre-heldout-v1.json")
    unseal.set_defaults(function=command_unseal)

    report = subparsers.add_parser("report")
    report.add_argument("--input", required=True)
    report.add_argument("--output", required=True)
    report.set_defaults(function=command_report)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--root", default=".")
    verify.set_defaults(function=command_verify)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
