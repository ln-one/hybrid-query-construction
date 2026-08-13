from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
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
    save_embedding_matrix,
)
from .storage import RankingStore, ranking_store_digest


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
) -> Path:
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
    ids_path, embeddings_path = save_embedding_matrix(
        corpus_path, encoder, cache / f"dense-{dense_key}-{dense_cache_id}"
    )
    document_ids = json.loads(ids_path.read_text(encoding="utf-8"))
    document_embeddings = np.load(embeddings_path, mmap_mode="r")

    collection_path, corpus_size = prepare_lucene_collection(corpus_path, cache / "lucene-docs")
    build_lucene_index(collection_path.parent, cache / "lucene-index")
    sparse_config = retriever_config["sparse"]
    sparse = SparseSearcher(
        cache / "lucene-index", sparse_config["k1"], sparse_config["b"], corpus_size
    )

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
        "generation_inputs": {
            name: sha256_file(path) if path is not None and path.exists() else None
            for name, path in generation_paths.items()
        },
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

    original_vectors = encoder.encode_queries(list(queries.values()), instruction)
    with RankingStore(store_path, dataset, document_ids) as store:
        for query_index, query_id in enumerate(queries):
            query = queries[query_id]
            original_vector = original_vectors[query_index]
            original_sparse_scores = sparse.scores(query)
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

            bridge_draws = sorted(draw for qid, draw in bridge if qid == query_id)
            for draw_id in bridge_draws:
                record = bridge[(query_id, draw_id)]
                all_references = _references_or_empty(record)
                digest = generation_digest(record)
                for reference_count in reference_counts:
                    references = all_references[:reference_count]
                    fallback = len(references) != reference_count
                    if fallback:
                        contextual = original_vector
                        residual = original_vector
                        rewrite_scores = original_sparse_scores
                    else:
                        contextual_vectors = encoder.encode_queries(
                            [f"{query} [SEP] {reference}" for reference in references],
                            instruction,
                        )
                        contextual = contextual_mean(contextual_vectors)
                        residual = orthogonal_residual(original_vector, contextual_vectors)
                        rewrite_scores = sparse.scores(
                            primary_sparse_rewrite(query, references)
                        )
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
        "ranking_store_sha256": ranking_store_digest(store_path),
    }
    manifest_name = (
        "rankings-manifest.json" if run_id == "primary" else f"rankings-{run_id}-manifest.json"
    )
    write_json(cache / manifest_name, manifest)
    return store_path
