# Contributing

Thank you for improving Jules Mission Ω!

## Ground rules
- Follow **Conventional Commits** (`feat:`, `fix:`, `docs:`).
- Every PR must include tests and docs updates where relevant.
- No secrets in code or CI logs. Use env vars.

## Dev setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev,neo4j]
pre-commit install
```

## Branching & PR flow
`feat/<scope>-<short>` or `fix/<scope>-<short>`

Run: `ruff`, `pytest`, `mypy`

Update vault docs if your change mutates code paths:
`jules-benchmark && jules-risk-scan && jules-vault-update`

Open PR with:
- Summary (what/why)
- Testing notes
- Risk (fallback, entropy)

Tick “I updated docs/FEATURES.md or docs/BUGFIXES.md”

## Testing matrix
- Python 3.10–3.12
- Minimal services mocked (no external calls in unit tests)
- API contract: json-schema stable; add new fields backwards-compatible

## Code style & quality
- `ruff`, `black`, `isort`, `mypy`
- Limit public API surface; keep internal functions private (`_name`)
- Favor pure functions; isolate I/O at edges

## PR checklist
- [ ] Tests pass (CI)
- [ ] Docs updated (README/FEATURES/BUGFIXES/VAULT)
- [ ] API contract compatible (if applicable)
- [ ] No secrets / PII