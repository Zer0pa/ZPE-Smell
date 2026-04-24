# Reproducibility

## Canonical Inputs

- `src/zpe_smell/codec.py` deterministically constructs the surrogate receptor-response model and the fixed 35-episode corpus used for the public replay.
- `proofs/artifacts/public_smell_surrogate_scope.json` is the committed authority artifact for the bounded public result.
- `validation/results/reference_public_eval.json` is the committed exact-match replay target for the public evaluation command.
- `docs/SCOPE.md` defines the declared bounded surface used to interpret the public result.

No external dataset download is required for the public replay surface.

## Golden-Bundle Hash

Placeholder: will be populated by the `receipt-bundle.yml` workflow in Wave 3.

## Verification Command

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e '.[dev]'
python3 -m zpe_smell.reproduce --output validation/results/latest_public_eval.json
python3 -m pytest -q
```

## Supported Runtimes

- Python 3.11+.
- Local macOS and Linux shells with a standard Python toolchain.
- No external services or non-Python system libraries are required for the bounded public replay.
