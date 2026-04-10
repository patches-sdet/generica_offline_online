# Tests Scaffold

This scaffold mirrors the current registry-first, deterministic rebuild architecture.

Suggested migration path:

1. Delete tracked `__pycache__` and `*.pyc` files from the repo.
2. Archive or remove legacy `.old` modules from live package paths.
3. Replace the existing `tests/` tree with this scaffold gradually.
4. Start by making the smoke and regression suites pass.

Recommended commands:

```bash
pytest tests/smoke -q
pytest tests/regression -q
pytest tests/unit -q
pytest tests/blackbox -q
pytest -q
```