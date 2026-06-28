# Contributing

## Principles

- keep interfaces stable and implementations replaceable
- prefer declarative reasoning graphs over hidden control flow
- add tests for every behavioral change
- document architecture changes before broad implementation

## Development

```bash
uv sync
uv run ruff check .
uv run black --check .
uv run mypy .
uv run pytest
```

## Pull Requests

- describe the problem and the intended outcome
- link code changes back to `C3_SPEC.md`
- include tests or explain why tests are not applicable
- keep operator behavior explicit and observable
