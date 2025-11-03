# Contributing to Coremon

Thanks for your interest in improving Coremon! Contributions of all kinds are welcome—bug reports, feature ideas, documentation, tests, and code changes.

If you’re ever unsure about anything, please ask questions. We’d rather answer early than rework later.

## Ways to contribute

- Report bugs and edge cases
- Propose or discuss new features
- Improve documentation and examples
- Add or improve tests
- Refactor code for clarity or performance
- Help triage issues and review PRs

## Ground rules

- Be respectful, inclusive, and constructive.
- Prefer small, focused changes over large, sweeping ones.
- Communicate early: open an issue or draft PR to validate direction.
- Write clear commit messages and PR descriptions.
- Add tests or docs when behavior changes.
- Follow the existing style and conventions in the repo.

## Getting help

- Not sure where to start? Open a “question” issue describing your goal.
- Unsure about project setup or commands? Ask—we’re happy to help.
- Can’t reproduce a bug? Share your environment details and steps tried.

## Before you start

- Review the README for project overview, setup, and usage.
- Look for existing issues and pull requests related to your change.
- If your change is non-trivial, please open an issue first to discuss.

## Development setup

Every environment is a little different. As a starting point:
- Check the README for setup instructions.
- Look for a Makefile, justfile, or package scripts for common tasks.
- If the repository includes formatters/linters, run them before committing (e.g., Black, Ruff/Flake8, isort, mypy).
- If in doubt about how to run or test the project, please ask or open a “question” issue.

## Reporting bugs

Please include:
- A clear, descriptive title
- Steps to reproduce (minimal repro if possible)
- What you expected to happen vs. what actually happened
- Environment details (OS, Python version, dependencies, relevant configuration)
- Logs, screenshots, or error messages if available

## Suggesting enhancements

Please include:
- The problem you’re trying to solve (use-case)
- Why the change benefits users
- Any alternatives you considered
- Rough proposal of the API/UX, if relevant

## Pull requests

- Branch from the latest `main`.
- Keep PRs small and focused; one change per PR is best.
- Include tests and documentation updates when behavior changes.
- Link related issues (e.g., “Fixes #123”).
- Mark WIP/Draft if you’re seeking early feedback.

PR checklist:
- Code builds locally and tests pass
- Linters/formatters have been run
- Docs/README updated if behavior or config changes
- Breaking changes are clearly called out

## Commit messages

- Use clear, descriptive messages (e.g., “fix: handle empty config path”).
- Conventional Commits are welcome but not required—clarity is.
- Reference issues when applicable (e.g., “Refs #123”).

## Code style and tests

- Match the existing style in the codebase.
- Prefer readability and maintainability.
- Add or update tests for new or changed behavior.
- Keep CI green; if a job is failing and you’re unsure why, ask for help.

## Issue triage and labels

If you’re helping triage:
- Confirm repro steps and add details
- Apply labels to help categorize (bug, enhancement, question, good first issue, etc.)
- Close duplicates linking to the canonical issue
- Be kind and welcoming to newcomers

## Security

If you discover a security vulnerability, please do not open a public issue. Instead, disclose it privately:
- Use GitHub’s private vulnerability reporting if enabled, or
- Email the maintainer(s) listed in the repo, or
- Otherwise, open a minimal “security” issue asking for a private contact channel.

## Licensing

By contributing, you agree that your contributions will be licensed under the same license as this repository. If you need clarification, please ask before submitting your PR.

## Thanks

Thank you for helping improve Coremon! Your time and contributions are greatly appreciated. If you’re uncertain about anything at all—just ask.
