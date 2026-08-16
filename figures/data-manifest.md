# Figure data manifest

| Figure | Claim supported | Input | Script | Status |
|---|---|---|---|---|
| F1 | fixed-$L=50$ changes to the query-level DESA-versus-Original judgment | controlled complete and fixed-cutoff JSONL files in `artifacts/results/raw/` | `figures/results/fig_fixed_top_l_diagnostics.py` | generated (PNG/SVG/PDF; main text) |
| F2 | quality/access trade-off, including matched QuDAR-simple | `report/main-results.csv`; `report/qudar-baseline-results.csv` | `figures/results/fig_quality_access_tradeoff.py` | generated; removed from manuscript as redundant with Table 1 |
| F3 | channel depth distributions | T2 per-query | report builder | planned |
| F4 | nested corpus scale trend | scale per-query | report builder | planned |
| F5 | realized Dense drift and Sparse reordering | `figures/data/mechanism-distributions.csv` | `figures/mechanism/fig_mechanism_distributions.py` | generated (PNG/SVG/PDF; main text) |
| F6 | mechanism magnitude versus isolated quality/access effects | `figures/data/mechanism-binned-effects.csv` | `figures/mechanism/fig_mechanism_binned_effects.py` | generated (PNG/SVG/PDF; appendix) |

No synthetic planning values are permitted in final figure inputs.
