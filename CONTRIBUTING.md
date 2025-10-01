# Contributing to Jules Mission Ω (optimizer)

Thanks for your interest in improving Jules Mission Ω! We welcome contributions of all kinds—bug reports, docs, tests, features, and ops hardening. This guide explains how to get set up, how we work, and what "good" looks like here.

## TL;DR (Join Protocol)

Fork → branch → commit (Conventional Commits) → PR → pass CI → human review → merge (GitHub Flow).

Follow the [Code of Conduct](#code-of-conduct) (Contributor Covenant v2.1).

Use [SemVer](#versioning--releases) for releases, [Black](#style-lint-tests) + [Ruff](#style-lint-tests) for code style, and [pre-commit hooks](#pre-commit-format--lint-before-each-commit) locally.

## Code of Conduct

We follow the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold these standards. Please report unacceptable behavior to the maintainers.

## Development Workflow

We use [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow): small, frequent branches off `main`, open a PR early, iterate with review, and merge once green. Protected branches may enforce linear history.

### Steps

1. Fork the repo and clone your fork.
2. Create a branch: `git checkout -b feat/my-improvement`
3. Run locally (see [Setup](#local-setup) below), commit using [Conventional Commits](#commit-messages), push your branch, and open a PR.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) to make history and changelogs clearer:

```
feat(mcp): add capability-based routing for code_generation
fix(vm): handle docker build error on missing requirements.txt
docs(api): clarify /agent/execute request schema
```

Common types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`.

## Versioning & Releases

We follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):

- **MAJOR** for incompatible changes
- **MINOR** for backward-compatible features
- **PATCH** for backward-compatible bug fixes

## Local Setup

### Prerequisites

- Python 3.9+ (3.11+ recommended)
- Docker (for VM/container flows)
- (Optional) Redis, Postgres, Neo4j if you're exercising those integrations

### Install

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"  # or: pip install -r requirements.txt
cp .env.example .env     # add your keys and local config
```

### Pre-commit (format & lint before each commit)

```bash
pip install pre-commit
pre-commit install
```

Run manually on all files:
```bash
pre-commit run --all-files
```

We use [Black](https://black.readthedocs.io/en/stable/) for formatting and [Ruff](https://docs.astral.sh/ruff/) for linting; both run via pre-commit hooks.

### Run API

```bash
uvicorn optimizer.api.main:app --reload --host 0.0.0.0 --port 8080
```

Swagger UI at: http://localhost:8080/docs

### Test & Smoke

```bash
pytest -q
bash scripts/smoke_test.sh
```

## Project Areas & What to Touch

- **API** (`optimizer/api/*`): FastAPI app, routes, models
- **MCP** (`optimizer/mcp/server_manager.py`): multi-provider routing for OpenAI/Anthropic/Gemini/Local
- **VM/Containers** (`optimizer/vm_integration/enhanced_vm_manager.py`): repo clone + build + run
- **Ops** (`systemd/.service`, `docker/`, `scripts/*`): service units, smoke tests, CI

Please keep modules small and composable; prefer adding new units over monolith changes.

## Style, Lint, Tests

- **Formatter**: [Black](https://black.readthedocs.io/en/stable/) (no bikeshedding)
- **Linter**: [Ruff](https://docs.astral.sh/ruff/) (fast, includes many Flake/Isort rules)
- **Tests**: [Pytest](https://docs.pytest.org/); write unit/integration tests for new logic and for bug fixes add a failing test first

Example:
```bash
black .
ruff check .
pytest -q
```

## Documentation

We practice **Docs as Code**. Update `docs/` (or in-file docstrings) alongside your change. If you're adding a major component, start with a brief spec in `specs/` and reference it in the PR. (Use PR templates—see below.)

## Security / Responsible Disclosure

Don't open issues for exploitable vulnerabilities. Instead, follow the `SECURITY.md` instructions (coordinated disclosure).

## Opening a Pull Request

Before opening a PR:

1. Ensure pre-commit, tests, and smoke tests pass
2. Write a clear PR title/description and link related issues
3. Include motivation, design, risks, and rollout/rollback
4. If you change APIs, update docs and add migration notes

Our CI runs on [GitHub Actions](https://docs.github.com/en/actions). Keep jobs minimal, cache deps, and fail fast.

We use [Pull Request templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository) and (optionally) CODEOWNERS for targeted review.

### What the PR Bot (Jules) Checks

- Lint/format/test status
- `scripts/smoke_test.sh` results
- Basic impact analysis notes (files touched, routes affected)
- (If applicable) systemd units validate and don't widen permissions

Automated checks are advisory unless they indicate correctness or security regressions.

## Issue Labels

`bug`, `feature`, `docs`, `good first issue`, `help wanted`, `infra`, `performance`, `security`

## Getting Help

Open a [GitHub Discussion](https://docs.github.com/en/discussions) or an Issue and tag maintainers. Be specific: "expected vs. actual," repro steps, logs, platform, and commit SHA.

## References / Standards

- [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) (Code of Conduct)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)
- [Black](https://black.readthedocs.io/en/stable/) (Python formatter)
- [Ruff](https://docs.astral.sh/ruff/) (Python linter)
- [pre-commit](https://pre-commit.com/) (hooks)
- [Pytest](https://docs.pytest.org/) (testing)
- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow) (branching)
- [GitHub community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
- [Developer Certificate of Origin](https://developercertificate.org/)

---

As requested, we also provide a ready-to-use `.pre-commit-config.yaml` and enhanced GitHub Actions workflow (`ci.yml`) to automate these standards.
