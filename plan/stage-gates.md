# Stage gates

## D0 — Protocol locked

Required: dataset, generator, retriever, method, fusion, statistics, failure policy,
and environment configs validate and have SHA-256 entries.

## D1 — Traceability

Every intended claim maps to an experiment and output artifact. Unsupported claims
are removed or explicitly classified as limitations.

## D2 — Data contracts

Per-query record schema, table schema, figure manifest, and tiny golden artifacts pass.

## D3 — Formal results

Raw logs, aggregation commands, tables, figures, and failure records exist for every
main and robustness experiment.

## D4 — Result decontamination

The report contains no planning values or development results presented as held-out.

## D5 — Verification

A clean environment reproduces tests and all report tables from released records.

