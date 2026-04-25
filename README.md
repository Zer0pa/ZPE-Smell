# ZPE-Smell

[![License: SAL v7.0](https://img.shields.io/badge/license-SAL%20v7.0-orange)](https://github.com/Zer0pa/ZPE-Smell/blob/main/LICENSE)

## What This Is
ZPE-Smell is a research-in-progress smell encoding repo built around a bounded surrogate receptor-response panel. It packages a standalone smell codec, a fixed 35-episode benchmark surface, and the committed evidence needed to reproduce that bounded result.

The current repo is useful now for audit and replication on that declared surface. It does not make a broad smell product claim, and it does not claim admission to the broader certified subset.

## Key Metrics
| Metric | Value | Baseline |
|---|---:|---|
| SPEARMAN_RHO | 0.9996 | reference |
| NN_AT_1 | 94.29% | reference |
| MIXTURE_COLLISION | 0.00% | gate (max 0.05) |
| FIBER_COLLISION | 0.00% | gate (max 0.05) |
| ADAPTATION_ALIAS | 0.00% | gate (max 0.20) |
| ATTACK_SUCCESS | 0.00% | gate (eq 0.00) |

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

## Bounded Verdict
This repo publishes the bounded public verdict carried by the committed proof artifact.

| Field | Value |
|-------|-------|
| Verdict | `bounded_adopter_on_surrogate_scope` |
| State Label | `research_in_progress` |
| Proof Source Commit | `48507cbfcdc5` |
| Certified Subset Admission | `NO` |
| Source | proofs/artifacts/public_smell_surrogate_scope.json |

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

### Open Boundaries
- This repo is intentionally bounded to a surrogate receptor-response panel.
- The result is public because it is reproducible and honest on that bounded surface.
- Broader smell claims remain out of scope, and the result is not claimed as admitted to the broader certified subset.

### Citation
Use [`CITATION.cff`](./CITATION.cff) for software citation metadata, and cite the committed proof artifact when discussing the bounded result.
