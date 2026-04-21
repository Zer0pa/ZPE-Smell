# Contributing

Thank you for taking this repo seriously.

## Scope
- Keep contributions inside the declared surrogate receptor-response scope.
- Do not widen claims in code or docs without new committed evidence.
- Do not turn bounded benchmark success into a product claim or a broad smell claim.

## Development
- Use Python 3.11 or newer.
- Install with `pip install -e '.[dev]'`.
- Run `pytest -q` before proposing changes.
- If code changes alter benchmark outputs, regenerate the public artifact and update the proof anchors in the same change.

## Pull requests
- Keep changes atomic.
- Explain any metric movement plainly.
- Preserve the repo's public non-claims.
