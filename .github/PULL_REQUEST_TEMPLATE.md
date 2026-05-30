## Description

<!-- What does this PR do? Link related issues with "Closes #NNN" -->

Closes #

## Type of Change

- [ ] 🐛 Bug fix (non-breaking)
- [ ] ✨ New feature (non-breaking)
- [ ] 💥 Breaking change (fix or feature that changes existing behavior)
- [ ] 📝 Documentation only
- [ ] ♻️ Refactor (no behavior change)
- [ ] 🧪 Tests only
- [ ] 🔧 Chore / maintenance

## Changes Made

<!-- Brief bullet list of what changed -->
-
-

## How to Test

```bash
# Commands to verify this PR works
uv run pytest tests/ -v
vlang compile examples/hello.vpl
```

**Test output:**
```
<!-- Paste test output here -->
```

## Checklist

- [ ] I've read [CONTRIBUTING.md](../CONTRIBUTING.md)
- [ ] My commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] I've added tests for new behavior (or explained why not)
- [ ] All existing tests pass (`uv run pytest tests/ -v`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] Type checking passes (`uv run mypy src/vlang --strict`)
- [ ] I've updated docs if needed (`docs/`)
- [ ] I've updated `CHANGELOG.md` under `[Unreleased]`

## Screenshots / Output

<!-- For language features: show a .vpl program and its output -->
<!-- For CLI changes: show before/after -->
