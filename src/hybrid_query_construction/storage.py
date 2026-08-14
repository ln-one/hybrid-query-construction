from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import zstandard as zstd

from .io import canonical_json, sha256_bytes


@dataclass(frozen=True)
class RankingArtifact:
    dataset: str
    query_id: str
    draw_id: int
    track: str
    channel: str
    reference_count: int
    ranking: tuple[str, ...]
    support: int
    fallback: bool
    generation_sha256: str
    ranking_sha256: str


@dataclass(frozen=True)
class RankingReuseEvidence:
    source: str
    selected: int
    inserted: int
    already_present: int
    ordinal_rows_verified: int
    selection_sha256: str


class RankingStore:
    """Compact, resumable storage for complete rankings.

    Document identifiers are stored once. Each ranking is a compressed array of
    integer document ordinals, so formal full-list artifacts remain practical to
    hash, copy, and audit.
    """

    def __init__(self, path: Path, dataset: str, document_ids: Sequence[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.dataset = dataset
        self.document_ids = tuple(document_ids)
        if len(set(self.document_ids)) != len(self.document_ids):
            raise ValueError("document identifiers must be unique")
        self.ordinals = {document_id: index for index, document_id in enumerate(document_ids)}
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=FULL")
        self._create_schema()
        self._verify_documents()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS rankings (
                dataset TEXT NOT NULL,
                query_id TEXT NOT NULL,
                draw_id INTEGER NOT NULL,
                track TEXT NOT NULL,
                channel TEXT NOT NULL,
                reference_count INTEGER NOT NULL,
                ranking BLOB NOT NULL,
                support INTEGER NOT NULL,
                fallback INTEGER NOT NULL,
                generation_sha256 TEXT NOT NULL,
                ranking_sha256 TEXT NOT NULL,
                PRIMARY KEY (dataset, query_id, draw_id, track, channel, reference_count)
            );
            """
        )
        self.connection.commit()

    def _verify_documents(self) -> None:
        payload = canonical_json(self.document_ids).encode()
        digest = sha256_bytes(payload)
        existing = self.connection.execute(
            "SELECT value FROM metadata WHERE key='documents_sha256'"
        ).fetchone()
        if existing and existing[0] != digest:
            raise RuntimeError("ranking store was created for a different document collection")
        self.connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES('dataset', ?)",
            (self.dataset,),
        )
        self.connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES('documents_json', ?)",
            (json.dumps(self.document_ids, ensure_ascii=False),),
        )
        self.connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES('documents_sha256', ?)",
            (digest,),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        self.connection.close()

    def __enter__(self) -> RankingStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @staticmethod
    def load_document_ids(path: Path) -> tuple[str, ...]:
        connection = sqlite3.connect(path)
        try:
            row = connection.execute(
                "SELECT value FROM metadata WHERE key='documents_json'"
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            raise RuntimeError(f"missing documents metadata in {path}")
        return tuple(json.loads(row[0]))

    def has(
        self,
        *,
        query_id: str,
        draw_id: int,
        track: str,
        channel: str,
        reference_count: int,
    ) -> bool:
        row = self.connection.execute(
            """SELECT 1 FROM rankings WHERE dataset=? AND query_id=? AND draw_id=?
            AND track=? AND channel=? AND reference_count=?""",
            (self.dataset, query_id, draw_id, track, channel, reference_count),
        ).fetchone()
        return row is not None

    def put(
        self,
        *,
        query_id: str,
        draw_id: int,
        track: str,
        channel: str,
        reference_count: int,
        ranking: Sequence[str],
        support: int,
        fallback: bool,
        generation_sha256: str,
    ) -> str:
        if len(set(ranking)) != len(ranking):
            raise ValueError("ranking contains duplicate document identifiers")
        try:
            array = np.asarray([self.ordinals[item] for item in ranking], dtype="<u4")
        except KeyError as error:
            raise ValueError(f"ranking contains unknown document: {error.args[0]}") from error
        raw = array.tobytes()
        digest = sha256_bytes(raw)
        compressed = zstd.ZstdCompressor(level=9).compress(raw)
        self.connection.execute(
            """INSERT OR REPLACE INTO rankings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                self.dataset,
                query_id,
                draw_id,
                track,
                channel,
                reference_count,
                compressed,
                support,
                int(fallback),
                generation_sha256,
                digest,
            ),
        )
        self.connection.commit()
        return digest

    def get(
        self,
        *,
        query_id: str,
        draw_id: int,
        track: str,
        channel: str,
        reference_count: int,
    ) -> RankingArtifact:
        row = self.connection.execute(
            """SELECT ranking, support, fallback, generation_sha256, ranking_sha256
            FROM rankings WHERE dataset=? AND query_id=? AND draw_id=? AND track=?
            AND channel=? AND reference_count=?""",
            (self.dataset, query_id, draw_id, track, channel, reference_count),
        ).fetchone()
        if row is None:
            raise KeyError((query_id, draw_id, track, channel, reference_count))
        raw = zstd.ZstdDecompressor().decompress(row[0])
        if sha256_bytes(raw) != row[4]:
            raise RuntimeError("ranking artifact hash mismatch")
        indices = np.frombuffer(raw, dtype="<u4")
        ranking = tuple(self.document_ids[int(index)] for index in indices)
        return RankingArtifact(
            dataset=self.dataset,
            query_id=query_id,
            draw_id=draw_id,
            track=track,
            channel=channel,
            reference_count=reference_count,
            ranking=ranking,
            support=int(row[1]),
            fallback=bool(row[2]),
            generation_sha256=str(row[3]),
            ranking_sha256=str(row[4]),
        )

    def keys(self) -> Iterator[tuple[str, int, str, str, int]]:
        rows = self.connection.execute(
            """SELECT query_id, draw_id, track, channel, reference_count FROM rankings
            WHERE dataset=? ORDER BY query_id, draw_id, track, channel, reference_count""",
            (self.dataset,),
        )
        yield from rows

    def copy_verified_from(
        self,
        source_path: Path,
        *,
        select: Callable[[tuple[str, int, str, str, int]], bool],
    ) -> RankingReuseEvidence:
        """Reuse exact rankings after verifying collection and ordinal identity.

        Rankings encode ordered document ordinals. Equal document metadata plus
        equal decompressed ordinal bytes therefore proves itemwise rank parity.
        Existing destination rows are never overwritten.
        """
        source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
        selected = inserted = already_present = verified = 0
        evidence: list[str] = []
        try:
            source_metadata = dict(source.execute("SELECT key, value FROM metadata").fetchall())
            destination_metadata = dict(
                self.connection.execute("SELECT key, value FROM metadata").fetchall()
            )
            for key in ("dataset", "documents_sha256", "documents_json"):
                if source_metadata.get(key) != destination_metadata.get(key):
                    raise RuntimeError(
                        f"cannot reuse rankings with different {key}: {source_path}"
                    )

            rows = source.execute(
                """SELECT dataset, query_id, draw_id, track, channel, reference_count,
                ranking, support, fallback, generation_sha256, ranking_sha256
                FROM rankings
                ORDER BY query_id, draw_id, track, channel, reference_count"""
            )
            for row in rows:
                key = (str(row[1]), int(row[2]), str(row[3]), str(row[4]), int(row[5]))
                if not select(key):
                    continue
                selected += 1
                raw = zstd.ZstdDecompressor().decompress(row[6])
                if sha256_bytes(raw) != row[10]:
                    raise RuntimeError(f"source ranking hash mismatch for {key}")
                ordinals = np.frombuffer(raw, dtype="<u4")
                if len(ordinals) and int(ordinals.max()) >= len(self.document_ids):
                    raise RuntimeError(f"source ranking has invalid ordinal for {key}")
                verified += 1

                existing = self.connection.execute(
                    """SELECT support, fallback, generation_sha256, ranking_sha256
                    FROM rankings WHERE dataset=? AND query_id=? AND draw_id=?
                    AND track=? AND channel=? AND reference_count=?""",
                    (self.dataset, *key),
                ).fetchone()
                metadata = (int(row[7]), int(row[8]), str(row[9]), str(row[10]))
                if existing is not None:
                    if tuple(existing) != metadata:
                        raise RuntimeError(f"existing ranking differs from reuse source: {key}")
                    already_present += 1
                else:
                    self.connection.execute(
                        """INSERT INTO rankings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        row,
                    )
                    inserted += 1
                evidence.append(canonical_json((*key, *metadata)))
            self.connection.commit()
        finally:
            source.close()
        return RankingReuseEvidence(
            source=str(source_path),
            selected=selected,
            inserted=inserted,
            already_present=already_present,
            ordinal_rows_verified=verified,
            selection_sha256=sha256_bytes("\n".join(evidence).encode()),
        )


def ranking_store_digest(path: Path) -> str:
    """Hash logical ranking contents, independent of SQLite page layout."""
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        metadata = connection.execute("SELECT key, value FROM metadata ORDER BY key").fetchall()
        rows = connection.execute(
            """SELECT dataset, query_id, draw_id, track, channel, reference_count,
            ranking, support, fallback, generation_sha256, ranking_sha256
            FROM rankings
            ORDER BY dataset, query_id, draw_id, track, channel, reference_count"""
        )
        parts = [canonical_json(metadata)]
        for row in rows:
            raw = zstd.ZstdDecompressor().decompress(row[6])
            if sha256_bytes(raw) != row[10]:
                raise RuntimeError("ranking artifact hash mismatch")
            parts.append(canonical_json((*row[:6], *row[7:])))
        return sha256_bytes("\n".join(parts).encode())
    finally:
        connection.close()
