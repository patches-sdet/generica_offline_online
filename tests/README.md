# Test Suite Guide

This repository has an active test suite organized around the current registry-first, deterministic rebuild architecture.

## Test Layout

- [`tests/smoke/`](tests/smoke) for bootstrap and basic execution checks
- [`tests/regression/`](tests/regression) for deterministic rebuild and content reload invariants
- [`tests/unit/`](tests/unit) for application, calculations, content, effects, and runtime behavior
- [`tests/blackbox/`](tests/blackbox) for outcome-oriented behavior checks

The live pytest configuration is defined in [`pytest.ini`](pytest.ini:1).

## Run the Full Suite

Preferred with uv:

```bash
uv run pytest
```

Direct pytest also works in an environment where the project dependencies are already installed:

```bash
pytest
```

## Run Targeted Suites

```bash
uv run pytest tests/smoke -q
uv run pytest tests/regression -q
uv run pytest tests/unit -q
uv run pytest tests/blackbox -q
```

## Coverage and CI

CI is defined in [`.github/workflows/test.yml`](.github/workflows/test.yml:1).

The workflow currently:
- runs on push and pull request
- tests against Python 3.10, 3.11, and 3.12
- runs coverage with `pytest-cov`
- enforces `coverage report --fail-under=70`

Local coverage example:

```bash
uv run pytest tests/ -v --cov=src --cov-report=term-missing
```

## Current Known Gap

Phase 1 documentation cleanup does not change runtime behavior. Runtime placeholder tests remain Phase 2 work and should be implemented separately from documentation updates.
