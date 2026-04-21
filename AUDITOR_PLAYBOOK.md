# Auditor Playbook

This is the shortest honest path to falsify the public repo surface.

## Steps
1. Create a virtual environment and install the repo with `python3 -m pip install -e '.[dev]'`.
2. Reproduce the public artifact with `python3 -m zpe_smell.reproduce --output validation/results/latest_public_eval.json`.
3. Run `python3 -m pytest -q`.
4. Compare `validation/results/latest_public_eval.json` to `proofs/artifacts/public_smell_surrogate_scope.json`.
5. Read `docs/SCOPE.md` and `PUBLIC_AUDIT_LIMITS.md` before drawing any conclusion beyond the fixed surrogate surface.

## What a valid dispute looks like
- A reproduced metric differs from the committed proof artifact.
- A proof anchor path is missing or non-runnable.
- The docs overclaim beyond the bounded surrogate receptor-response scope.
