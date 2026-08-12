from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from .datasets import load_queries, prepare_beir_dataset, unseal_qrels
from .generation import run_generation
from .locking import create_preheldout_lock
from .reporting import build_report
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
    if args.limit:
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
    )


def command_lock(args: argparse.Namespace) -> None:
    root = repository_root()
    print(json.dumps(create_preheldout_lock(root, root / args.output), indent=2))


def command_unseal(args: argparse.Namespace) -> None:
    root = repository_root()
    print(unseal_qrels(args.dataset, root, root / args.lock))


def command_report(args: argparse.Namespace) -> None:
    print(build_report(Path(args.input), Path(args.output)))


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
    generate.set_defaults(function=command_generate)

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
