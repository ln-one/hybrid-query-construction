from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from .datasets import load_queries
from .fusion import rank_scores
from .generation import current_commit
from .io import canonical_json, read_jsonl, sha256_bytes, sha256_file, write_json
from .java import ensure_java_runtime
from .methods import (
    contextual_mean,
    mugi_sparse_rewrite,
    orthogonal_residual,
    primary_sparse_rewrite,
    query2doc_sparse_rewrite,
    reference_mean,
    sparse_boolean_mask,
    sparse_score_product,
)
from .models import GenerationRecord
from .retrieval import (
    DenseEncoder,
    SparseSearcher,
    build_lucene_index,
    dense_ranking,
    prepare_lucene_collection,
    reuse_embedding_matrix,
    save_embedding_matrix,
)
from .storage import RankingReuseEvidence, RankingStore, ranking_store_digest

CONTROLLED_CHANNELS = (
    "dense_contextual",
    "dense_residual",
    "sparse_rewrite",
    "sparse_anchor",
    "sparse_mask",
    "sparse_references_only",
    "sparse_mugi",
)


def load_generations(path: Path | None) -> dict[tuple[str, int], GenerationRecord]:
    if path is None or not path.exists():
        return {}
    records: dict[tuple[str, int], GenerationRecord] = {}
    for row in read_jsonl(path):
        record = GenerationRecord.model_validate(row)
        key = (record.query_id, record.draw_id)
        if key in records:
            raise ValueError(f"duplicate generation record in {path}: {key}")
        records[key] = record
    return records


def generation_digest(record: GenerationRecord | None) -> str:
    if record is None:
        return "0" * 64
    return sha256_bytes(canonical_json(record.model_dump(mode="json")).encode())


def _put_ranking(
    store: RankingStore,
    document_ids: Sequence[str],
    document_embeddings: np.ndarray,
    query_vector: np.ndarray,
    *,
    query_id: str,
    draw_id: int,
    track: str,
    channel: str,
    reference_count: int,
    fallback: bool,
    generation_sha256: str,
) -> None:
    if store.has(
        query_id=query_id,
        draw_id=draw_id,
        track=track,
        channel=channel,
        reference_count=reference_count,
    ):
        return
    ranking = dense_ranking(document_ids, document_embeddings, query_vector)
    store.put(
        query_id=query_id,
        draw_id=draw_id,
        track=track,
        channel=channel,
        reference_count=reference_count,
        ranking=ranking,
        support=len(ranking),
        fallback=fallback,
        generation_sha256=generation_sha256,
    )


def _put_sparse(
    store: RankingStore,
    scores: Mapping[str, float],
    *,
    query_id: str,
    draw_id: int,
    track: str,
    channel: str,
    reference_count: int,
    fallback: bool,
    generation_sha256: str,
) -> None:
    if store.has(
        query_id=query_id,
        draw_id=draw_id,
        track=track,
        channel=channel,
        reference_count=reference_count,
    ):
        return
    ranking = rank_scores(scores)
    store.put(
        query_id=query_id,
        draw_id=draw_id,
        track=track,
        channel=channel,
        reference_count=reference_count,
        ranking=ranking,
        support=len(ranking),
        fallback=fallback,
        generation_sha256=generation_sha256,
    )


def _references_or_empty(record: GenerationRecord | None) -> tuple[str, ...]:
    if record is None or record.status != "ok":
        return ()
    return record.parsed_references


def build_rankings(
    *,
    root: Path,
    dataset: str,
    retriever_config: dict[str, Any],
    bridge_generation: Path | None = None,
    mugi_generation: Path | None = None,
    hyde_generation: Path | None = None,
    query2doc_generation: Path | None = None,
    query_limit: int | None = None,
    reference_counts: Sequence[int] = (1, 3, 5),
    dense_key: str = "dense",
    run_id: str = "primary",
    reuse_store: Path | None = None,
    reuse_mode: str = "none",
    reuse_embeddings_from: str | None = None,
) -> Path:
    if reuse_mode not in {"none", "base", "sparse"}:
        raise ValueError(f"unsupported ranking reuse mode: {reuse_mode}")
    if (reuse_store is None) != (reuse_mode == "none"):
        raise ValueError("--reuse-store and a non-none --reuse-mode must be used together")
    data_directory = root / "data" / "processed" / dataset
    ensure_java_runtime(int(retriever_config["sparse"]["java"]))
    corpus_path = data_directory / "corpus.jsonl"
    queries = load_queries(data_directory / "queries.jsonl")
    if query_limit:
        queries = {query_id: queries[query_id] for query_id in sorted(queries)[:query_limit]}

    cache = root / "artifacts" / "rankings" / dataset
    dense_config = retriever_config[dense_key]
    encoder = DenseEncoder(dense_config["model_id"], dense_config["revision"])
    dense_cache_id = sha256_bytes(canonical_json(dense_config).encode())[:12]
    dense_cache = cache / f"dense-{dense_key}-{dense_cache_id}"
    embedding_reuse_evidence: Path | None = None
    if reuse_embeddings_from is None:
        ids_path, embeddings_path = save_embedding_matrix(corpus_path, encoder, dense_cache)
    else:
        source_cache = root / "artifacts" / "rankings" / reuse_embeddings_from
        source_dense_cache = source_cache / f"dense-{dense_key}-{dense_cache_id}"
        ids_path, embeddings_path, embedding_reuse_evidence = reuse_embedding_matrix(
            corpus_path,
            root / "data" / "processed" / reuse_embeddings_from / "corpus.jsonl",
            source_dense_cache / "document_ids.json",
            source_dense_cache / "document_embeddings.npy",
            dense_cache,
        )
    document_ids = json.loads(ids_path.read_text(encoding="utf-8"))
    document_embeddings = np.load(embeddings_path, mmap_mode="r")

    bridge = load_generations(bridge_generation)
    mugi = load_generations(mugi_generation)
    hyde = load_generations(hyde_generation)
    query2doc = load_generations(query2doc_generation)
    store_name = "rankings.sqlite3" if run_id == "primary" else f"rankings-{run_id}.sqlite3"
    store_path = cache / store_name
    instruction = dense_config.get("query_instruction", "")

    generation_paths = {
        "bridge": bridge_generation,
        "mugi": mugi_generation,
        "hyde": hyde_generation,
        "query2doc": query2doc_generation,
    }
    run_spec = {
        "schema_version": 1,
        "protocol_version": "hqc-formal-v1",
        "dataset": dataset,
        "run_id": run_id,
        "dense_key": dense_key,
        "query_limit": query_limit,
        "reference_counts": list(reference_counts),
        "code_commit": current_commit(root),
        "retriever_config_sha256": sha256_bytes(canonical_json(retriever_config).encode()),
        "corpus_sha256": sha256_file(corpus_path),
        "queries_sha256": sha256_file(data_directory / "queries.jsonl"),
        "document_ids_sha256": sha256_file(ids_path),
        "document_embeddings_sha256": sha256_file(embeddings_path),
        "embedding_reuse": (
            None
            if embedding_reuse_evidence is None
            else json.loads(embedding_reuse_evidence.read_text(encoding="utf-8"))
        ),
        "generation_inputs": {
            name: sha256_file(path) if path is not None and path.exists() else None
            for name, path in generation_paths.items()
        },
        "ranking_reuse": (
            None
            if reuse_store is None
            else {
                "mode": reuse_mode,
                "source": str(reuse_store.relative_to(root)),
                "source_store_sha256": ranking_store_digest(reuse_store),
            }
        ),
    }
    spec_name = "rankings-spec.json" if run_id == "primary" else f"rankings-{run_id}-spec.json"
    spec_path = cache / spec_name
    if spec_path.exists():
        existing_spec = json.loads(spec_path.read_text(encoding="utf-8"))
        if existing_spec != run_spec:
            raise RuntimeError(
                f"ranking run specification changed; choose a new --run-id: {spec_path}"
            )
    elif store_path.exists():
        raise RuntimeError(
            f"ranking store has no immutable run specification; move it aside: {store_path}"
        )
    else:
        write_json(spec_path, run_spec)

    reuse_evidence: RankingReuseEvidence | None = None
    with RankingStore(store_path, dataset, document_ids) as store:
        if reuse_store is not None:
            if reuse_mode == "base":

                def selection(key: tuple[str, int, str, str, int]) -> bool:
                    return key[2] == "base"
            else:

                def selection(key: tuple[str, int, str, str, int]) -> bool:
                    return key[3].startswith("sparse_") and key[2] != "fidelity"

            reuse_evidence = store.copy_verified_from(reuse_store, select=selection)

        def missing(
            query_id: str,
            draw_id: int,
            track: str,
            channel: str,
            reference_count: int,
        ) -> bool:
            return not store.has(
                query_id=query_id,
                draw_id=draw_id,
                track=track,
                channel=channel,
                reference_count=reference_count,
            )

        dense_query_ids: list[str] = []
        sparse_needed = False
        for query_id in queries:
            bridge_draws = sorted(draw for qid, draw in bridge if qid == query_id)
            fidelity_draws = [
                (name, draw)
                for name, records in (("mugi", mugi), ("hyde", hyde), ("query2doc", query2doc))
                for qid, draw in records
                if qid == query_id
            ]
            needs_dense = missing(query_id, 0, "base", "dense_original", 0)
            needs_sparse = missing(query_id, 0, "base", "sparse_original", 0)
            needs_dense = needs_dense or any(
                missing(query_id, draw, "controlled", channel, count)
                for draw in bridge_draws
                for count in reference_counts
                for channel in ("dense_contextual", "dense_residual")
            )
            needs_sparse = needs_sparse or any(
                missing(query_id, draw, "controlled", channel, count)
                for draw in bridge_draws
                for count in reference_counts
                for channel in (
                    "sparse_rewrite",
                    "sparse_anchor",
                    "sparse_mask",
                    "sparse_references_only",
                    "sparse_mugi",
                )
            )
            for method_name, draw in fidelity_draws:
                record = {"mugi": mugi, "hyde": hyde, "query2doc": query2doc}[method_name][
                    (query_id, draw)
                ]
                count = (
                    len(_references_or_empty(record))
                    or {
                        "mugi": 5,
                        "hyde": 8,
                        "query2doc": 1,
                    }[method_name]
                )
                needs_dense = needs_dense or missing(
                    query_id, draw, "fidelity", f"dense_{method_name}", count
                )
                needs_sparse = needs_sparse or missing(
                    query_id, draw, "fidelity", f"sparse_{method_name}", count
                )
            if needs_dense:
                dense_query_ids.append(query_id)
            sparse_needed = sparse_needed or needs_sparse

        original_vectors = {}
        if dense_query_ids:
            vectors = encoder.encode_queries(
                [queries[query_id] for query_id in dense_query_ids], instruction
            )
            original_vectors = dict(zip(dense_query_ids, vectors, strict=True))

        sparse: SparseSearcher | None = None
        if sparse_needed:
            collection_path, corpus_size = prepare_lucene_collection(
                corpus_path, cache / "lucene-docs"
            )
            build_lucene_index(collection_path.parent, cache / "lucene-index")
            sparse_config = retriever_config["sparse"]
            sparse = SparseSearcher(
                cache / "lucene-index",
                sparse_config["k1"],
                sparse_config["b"],
                corpus_size,
            )

        for query_id in queries:
            query = queries[query_id]
            bridge_draws = sorted(draw for qid, draw in bridge if qid == query_id)
            has_work = query_id in original_vectors or any(
                missing(query_id, draw, "controlled", channel, count)
                for draw in bridge_draws
                for count in reference_counts
                for channel in CONTROLLED_CHANNELS
            )
            has_work = has_work or any(
                qid == query_id for records in (mugi, hyde, query2doc) for qid, _ in records
            )
            if not has_work:
                continue

            original_vector = original_vectors.get(query_id)
            if original_vector is None:
                original_vector = encoder.encode_queries([query], instruction)[0]
            needs_original_sparse = missing(query_id, 0, "base", "sparse_original", 0) or any(
                missing(query_id, draw, "controlled", channel, count)
                for draw in bridge_draws
                for count in reference_counts
                for channel in CONTROLLED_CHANNELS
                if channel.startswith("sparse_")
            )
            needs_original_sparse = needs_original_sparse or any(
                qid == query_id for records in (mugi, hyde, query2doc) for qid, _ in records
            )
            if needs_original_sparse:
                if sparse is None:
                    raise AssertionError("sparse searcher was not initialized")
                original_sparse_scores = sparse.scores(query)
            else:
                original_sparse_scores = {}

            if missing(query_id, 0, "base", "dense_original", 0):
                _put_ranking(
                    store,
                    document_ids,
                    document_embeddings,
                    original_vector,
                    query_id=query_id,
                    draw_id=0,
                    track="base",
                    channel="dense_original",
                    reference_count=0,
                    fallback=False,
                    generation_sha256="0" * 64,
                )
            if missing(query_id, 0, "base", "sparse_original", 0):
                _put_sparse(
                    store,
                    original_sparse_scores,
                    query_id=query_id,
                    draw_id=0,
                    track="base",
                    channel="sparse_original",
                    reference_count=0,
                    fallback=False,
                    generation_sha256="0" * 64,
                )
            for draw_id in bridge_draws:
                record = bridge[(query_id, draw_id)]
                all_references = _references_or_empty(record)
                digest = generation_digest(record)
                for reference_count in reference_counts:
                    dense_channels = ("dense_contextual", "dense_residual")
                    sparse_channels = tuple(
                        channel
                        for channel in CONTROLLED_CHANNELS
                        if channel.startswith("sparse_")
                    )
                    needs_dense = any(
                        missing(
                            query_id,
                            draw_id,
                            "controlled",
                            channel,
                            reference_count,
                        )
                        for channel in dense_channels
                    )
                    needs_sparse = any(
                        missing(
                            query_id,
                            draw_id,
                            "controlled",
                            channel,
                            reference_count,
                        )
                        for channel in sparse_channels
                    )
                    if not needs_dense and not needs_sparse:
                        continue
                    references = all_references[:reference_count]
                    fallback = len(references) != reference_count
                    if needs_dense and fallback:
                        contextual = residual = original_vector
                    elif needs_dense:
                        contextual_vectors = encoder.encode_queries(
                            [f"{query} [SEP] {reference}" for reference in references],
                            instruction,
                        )
                        contextual = contextual_mean(contextual_vectors)
                        residual = orthogonal_residual(original_vector, contextual_vectors)
                    if needs_dense:
                        _put_ranking(
                            store,
                            document_ids,
                            document_embeddings,
                            contextual,
                            query_id=query_id,
                            draw_id=draw_id,
                            track="controlled",
                            channel="dense_contextual",
                            reference_count=reference_count,
                            fallback=fallback,
                            generation_sha256=digest,
                        )
                        _put_ranking(
                            store,
                            document_ids,
                            document_embeddings,
                            residual,
                            query_id=query_id,
                            draw_id=draw_id,
                            track="controlled",
                            channel="dense_residual",
                            reference_count=reference_count,
                            fallback=fallback,
                            generation_sha256=digest,
                        )
                    if needs_sparse:
                        if sparse is None:
                            raise AssertionError("sparse searcher was not initialized")
                        rewrite_scores = (
                            original_sparse_scores
                            if fallback
                            else sparse.scores(primary_sparse_rewrite(query, references))
                        )
                        sparse_variants = {
                            "sparse_rewrite": rewrite_scores,
                            "sparse_anchor": sparse_score_product(
                                original_sparse_scores, rewrite_scores
                            ),
                            "sparse_mask": sparse_boolean_mask(
                                original_sparse_scores, rewrite_scores
                            ),
                        }
                        if fallback:
                            sparse_variants["sparse_references_only"] = original_sparse_scores
                            sparse_variants["sparse_mugi"] = original_sparse_scores
                        else:
                            sparse_variants["sparse_references_only"] = sparse.scores(
                                " ".join(references)
                            )
                            sparse_variants["sparse_mugi"] = sparse.scores(
                                mugi_sparse_rewrite(query, references, beta=4)
                            )
                        for channel, scores in sparse_variants.items():
                            _put_sparse(
                                store,
                                scores,
                                query_id=query_id,
                                draw_id=draw_id,
                                track="controlled",
                                channel=channel,
                                reference_count=reference_count,
                                fallback=fallback,
                                generation_sha256=digest,
                            )

            fidelity_records = (
                ("mugi", mugi),
                ("hyde", hyde),
                ("query2doc", query2doc),
            )
            for method_name, records in fidelity_records:
                draws = sorted(draw for qid, draw in records if qid == query_id)
                for draw_id in draws:
                    record = records[(query_id, draw_id)]
                    references = _references_or_empty(record)
                    digest = generation_digest(record)
                    fallback = not references
                    if method_name == "mugi":
                        reference_count = len(references) or 5
                        if fallback:
                            dense_vector = original_vector
                            sparse_scores = original_sparse_scores
                        else:
                            contextual_vectors = encoder.encode_queries(
                                [f"{query} [SEP] {reference}" for reference in references],
                                instruction,
                            )
                            dense_vector = contextual_mean(contextual_vectors)
                            sparse_scores = sparse.scores(
                                mugi_sparse_rewrite(query, references, beta=4)
                            )
                    elif method_name == "hyde":
                        reference_count = len(references) or 8
                        if fallback:
                            dense_vector = original_vector
                        else:
                            document_vectors = encoder.encode_documents(references)
                            dense_vector = reference_mean(document_vectors)
                        sparse_scores = original_sparse_scores
                    else:
                        reference_count = len(references) or 1
                        if fallback:
                            dense_vector = original_vector
                            sparse_scores = original_sparse_scores
                        else:
                            dense_vector = encoder.encode_queries(
                                [f"{query} [SEP] {references[0]}"], instruction
                            )[0]
                            sparse_scores = sparse.scores(
                                query2doc_sparse_rewrite(query, references[0])
                            )
                    _put_ranking(
                        store,
                        document_ids,
                        document_embeddings,
                        dense_vector,
                        query_id=query_id,
                        draw_id=draw_id,
                        track="fidelity",
                        channel=f"dense_{method_name}",
                        reference_count=reference_count,
                        fallback=fallback,
                        generation_sha256=digest,
                    )
                    _put_sparse(
                        store,
                        sparse_scores,
                        query_id=query_id,
                        draw_id=draw_id,
                        track="fidelity",
                        channel=f"sparse_{method_name}",
                        reference_count=reference_count,
                        fallback=fallback,
                        generation_sha256=digest,
                    )
    manifest = {
        **run_spec,
        "reuse_evidence": asdict(reuse_evidence) if reuse_evidence is not None else None,
        "ranking_store_sha256": ranking_store_digest(store_path),
    }
    manifest_name = (
        "rankings-manifest.json" if run_id == "primary" else f"rankings-{run_id}-manifest.json"
    )
    write_json(cache / manifest_name, manifest)
    return store_path
