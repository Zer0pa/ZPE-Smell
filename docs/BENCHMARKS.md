# Benchmarks

This repo compares the committed smell codec against two direct public comparators on the same fixed benchmark surface.

## Comparator set
- `ZPE-Smell`: the full public codec in `src/zpe_smell/`
- `Receptor-only`: the same benchmark surface scored with receptor values only
- `Geometry-only`: the same benchmark surface scored with base geometry only

## Current comparator result

| Approach | Spearman | NN@1 | Mixture Collision |
|---|---:|---:|---:|
| ZPE-Smell | 0.9996 | 94.29% | 0.00% |
| Receptor-only | 0.9648 | 85.71% | 14.06% |
| Geometry-only | 0.9862 | 88.57% | 7.19% |

## Boundary
- These are bounded benchmark comparators on the fixed surrogate receptor-response surface only.
- They are not market claims and they are not general smell claims.
