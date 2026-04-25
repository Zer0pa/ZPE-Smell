# ZPE-Smell

[![License: SAL v7.0](https://img.shields.io/badge/license-SAL%20v7.0-orange)](https://github.com/Zer0pa/ZPE-Smell/blob/main/LICENSE)

## What This Is

ZPE-Smell is a smell encoding codec built around a fixed, 35-episode surrogate receptor-response benchmark. On that declared surface, it reaches Spearman `0.9996` — versus `0.9648` for a receptor-only baseline and `0.9862` for a geometry-only baseline — with zero mixture collision, zero fiber collision, and zero adaptation alias. That result is public, reproducible, and CI-anchored. The full proof artifact regenerates exactly from the committed code.

ZPE-Smell is one of seventeen public encoding lanes in the Zer0pa ZPE portfolio. It is useful now for audit and replication on the declared benchmark surface. It is improving continuously.

## Key Metrics

| Metric | Value | Baseline |
|---|---:|---|
| SPEARMAN_RHO | 0.9996 | reference |
| NN_AT_1 | 94.29% | reference |
| MIXTURE_COLLISION | 0.00% | max 0.05 |
| FIBER_COLLISION | 0.00% | max 0.05 |
| ADAPTATION_ALIAS | 0.00% | max 0.20 |
| ATTACK_SUCCESS | 0.00% | eq 0.00 |

> Source: `proofs/artifacts/public_smell_surrogate_scope.json` · CI: `tests/test_public_surface.py::test_committed_artifacts_match_live_eval`

## Competitive Benchmarks

| Approach | Spearman | NN@1 | Mixture Collision |
|---|---:|---:|---:|
| **ZPE-Smell** | **0.9996** | **94.29%** | **0.00%** |
| Receptor-only | 0.9648 | 85.71% | 14.06% |
| Geometry-only | 0.9862 | 88.57% | 7.19% |

> Source: `proofs/artifacts/public_smell_surrogate_scope.json` · CI: `tests/test_public_surface.py::test_public_eval_beats_public_comparators`

## What We Prove

- On the fixed surrogate receptor-response benchmark surface, the codec preserves retrieval structure with Spearman `0.9996`.
- On that same surface, nearest-neighbor recall at 1 is `94.29%`.
- On the declared nuisance family cases, mixture collision, fiber collision, adaptation alias, and attack success all stay at `0.00%`.
- Image-prefixed nuisance streams do not break smell routing on the committed benchmark surface.
- The full public artifact can be regenerated from the code and matched exactly against the committed proof file.

## What We Don't Claim

- We do not claim a digital smell product.
- We do not claim anything beyond the surrogate receptor-response scope shipped here.
- We do not claim this result is admitted to the broader certified subset.
- We do not claim coverage of a full empirical receptor panel or general smell perception.
- This scope is intentional, not a limitation in progress — broader claims will be named explicitly when they are earned.

## Bounded Verdict

This repo publishes the bounded public verdict carried by the committed proof artifact.

| Field | Value |
|-------|-------|
| Verdict | `STAGED` |
| Posture | `bounded_adopter_on_surrogate_scope` |
| State Label | `research_in_progress` |
| Certified Subset Admission | `NO` |
| Proof Source Commit | `48507cbfcdc5` |
| Source | `proofs/artifacts/public_smell_surrogate_scope.json` |

## Tests and Verification

| Code | Check | Verdict |
|---|---|---|
| V_01 | Full-panel roundtrip keeps all eight receptor channels intact | PASS |
| V_02 | Image-prefixed nuisance streams still route as smell on the fixed bundle surface | PASS |
| V_03 | Public evaluation keeps the bounded-scope verdict and all gates in pass state | PASS |
| V_04 | Public evaluation beats the receptor-only and geometry-only comparators on the committed surface | PASS |
| V_05 | Live evaluation matches the committed proof and reference artifacts exactly | PASS |

## Proof Anchors Used by CI

| Path | CI Check |
|---|---|
| `proofs/artifacts/public_smell_surrogate_scope.json` | V_05 |
| `validation/results/reference_public_eval.json` | V_05 |

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e '.[dev]'
python3 -m zpe_smell.reproduce --output validation/results/latest_public_eval.json
python3 -m pytest -q
```

## Citation

Use [`CITATION.cff`](./CITATION.cff) for software citation metadata, and cite the committed proof artifact when discussing the bounded result.
