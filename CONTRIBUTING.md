# Contributing

Thanks for helping with Stow for Stash. Bug reports and pull requests are welcome.

## Contribution licence

Every contribution is licensed under the terms in
[CONTRIBUTION-LICENSE.md](CONTRIBUTION-LICENSE.md) ([Deutsch](CONTRIBUTION-LICENSE.de.md);
Apache-2.0 for your contribution, GPL-3.0-only for the project as a whole). You accept it by
ticking the licence box in the pull request description. On GitHub, the
`Contribution licence declaration` check fails until the box is ticked. If several people author
a pull request, each of them adds a `Signed-off-by:` line with their own email address to their
commits.

## Commit messages

Commit messages and pull request titles follow
[Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`, with
one of `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore` or
`revert`. The subject has at most 100 characters.

## Before you push

Use Node.js 26 (see `.nvmrc`) and Python 3, then run:

```bash
pnpm install --frozen-lockfile
pnpm format:check && pnpm lint && pnpm test && pnpm build:check
```

If you change `version` in `plugins/stow/stow.yml`, change `VERSION` in `plugins/stow/stow.py`
too. A test checks that they match. Do not commit credentials.
