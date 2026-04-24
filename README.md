# ZPE-Smell

[![License: SAL v7.0](https://img.shields.io/badge/license-SAL%20v7.0-orange)](https://github.com/Zer0pa/ZPE-Smell/blob/main/LICENSE)

## What This Is
ZPE-Smell is a research-in-progress smell encoding repo built around a bounded surrogate receptor-response panel. It packages a standalone smell codec, a fixed 35-episode benchmark surface, and the committed evidence needed to reproduce that bounded result.

The current repo is useful now for audit and replication on that declared surface, and improving continuously. It does not make a broad smell product claim, and it does not claim admission to the broader certified subset.

| Field | Value |
|-------|-------|
| Architecture | SMELL_STREAM |
| Encoding | SMELL_SURROGATE_PANEL_V1 |

## Key Metrics
| Metric | Value | Baseline |
|---|---:|---|
| SPEARMAN_RHO | 0.9996 | reference |
| NN_AT_1 | 94.29% | reference |
| MIXTURE_COLLISION | 0.00% | gate |
| ATTACK_SUCCESS | 0.00% | gate |

> Source: `proofs/artifacts/public_smell_surrogate_scope.json`

## Competitive Benchmarks
| Approach | Spearman | NN@1 | Mixture Collision |
|---|---:|---:|---:|
| **ZPE-Smell** | **0.9996** | **94.29%** | **0.00%** |
| Receptor-only | 0.9648 | 85.71% | 14.06% |
| Geometry-only | 0.9862 | 88.57% | 7.19% |

> Source: `proofs/artifacts/public_smell_surrogate_scope.json`

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

## Commercial Readiness
This release candidate is restamped to the verified source commit below.

| Field | Value |
|-------|-------|
| Verdict | STAGED |
| Commit SHA | 48507cbfcdc5 |
| Confidence | 100% |
| Source | proofs/artifacts/public_smell_surrogate_scope.json |

## Tests and Verification
| Code | Check | Verdict |
|---|---|---|
| V_01 | Full-panel roundtrip keeps all eight receptor channels intact | PASS |
| V_02 | Image-prefixed nuisance streams still route as smell on the fixed bundle surface | PASS |
| V_03 | Live evaluation matches the committed public proof artifact exactly | PASS |

## Proof Anchors
| Path | State |
|---|---|
| `proofs/artifacts/public_smell_surrogate_scope.json` | VERIFIED |
| `validation/results/reference_public_eval.json` | VERIFIED |
| `proofs/manifests/CURRENT_AUTHORITY_PACKET.md` | VERIFIED |

## Repo Shape
| Field | Value |
|---|---|
| Proof Anchors | 3 |
| Modality Lanes | 1 |
| Authority Source | `proofs/artifacts/public_smell_surrogate_scope.json` |
| Package | `src/zpe_smell` |

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
