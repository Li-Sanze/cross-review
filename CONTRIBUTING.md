# Contributing to CrossReview

Thank you for your interest in contributing! This guide covers the process for different types of contributions.

## Contribution Tiers

| Tier | Examples | Requirements |
|------|----------|-------------|
| **Fix** | Bug fixes, typos, doc clarifications | Open issue first, include test |
| **Enhancement** | Improve existing feature behavior | Open issue first, discuss approach |
| **Feature** | New CLI flags, new artifact types, schema changes | Open issue first, get approval before coding |

## Before You Start

1. **Open an issue first.** Describe the problem or proposal. Don't start coding until the approach is agreed upon.
2. **Check existing issues and roadmap** in `.sopify-skills/blueprint/tasks.md`.

## Development Setup

```bash
git clone https://github.com/evidentloop/cross-review.git
cd cross-review
pip install -e '.[dev]'
```

## Running Tests

```bash
pytest tests/ -x -q
```

## Linting

```bash
ruff check crossreview/ tests/
```

## Pull Request Process

1. Branch from `main` (use `fix/`, `feat/`, or `docs/` prefix).
2. Write or update tests for your changes.
3. Ensure `pytest` and `ruff check` pass locally.
4. Open a PR against `main`.
5. Describe **what** changed and **why** in the PR body.

## Code Style

- Follow existing patterns in the codebase.
- `ruff` enforces formatting — fix any lint errors before submitting.
- Keep functions focused and testable.

## What We Don't Accept

- Changes that break the deterministic adjudicator contract.
- Dependencies beyond `pyyaml` in core (optional extras are fine).
- Schema changes without an issue and design discussion.

## Eval Fixtures

Eval data lives on the `eval-data` branch, not `main`. If your change affects review quality, add or update fixtures there.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
