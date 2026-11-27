# Releasing

Push a `v*` tag to release. Merging PRs or pushing to `main` only runs CI; nothing is published.

## First release: configure PyPI trusted publishing

Before the first tag, add a pending publisher at <https://pypi.org/manage/account/publishing/>:

- PyPI project name: `bnbingo`
- Owner: `levontumanyan`
- Repository name: `bnbingo`
- Workflow name: `release.yml`
- Environment name: `pypi`

Without this, the `publish` job will fail at `uv publish`.

## Steps

1. Bump `__version__` in `bnbingo/__init__.py` (the sole version source; `pyproject.toml` reads it dynamically). Pick a version above the current PyPI release — PyPI versions are immutable.
2. Commit and push to `main`; wait for CI to pass.
3. Push a tag matching the version:

   ```sh
   git tag vX.Y.Z && git push origin vX.Y.Z
   ```

   If `git push` hangs in a non-interactive shell, create the ref via the API:

   ```sh
   SHA=$(git rev-parse HEAD)
   curl -X POST https://api.github.com/repos/levontumanyan/bnbingo/git/refs \
     -H "Authorization: Bearer $(gh auth token)" \
     -H "Accept: application/vnd.github+json" \
     -d "{\"ref\":\"refs/tags/vX.Y.Z\",\"sha\":\"$SHA\"}"
   ```

`.github/workflows/release.yml` then validates the tag against `__version__`, runs tests, builds and verifies the sdist/wheel, smoke-tests the installed wheel, publishes to PyPI via OIDC (environment `pypi`), and creates a GitHub Release with the artifacts attached.

Verify at <https://pypi.org/project/bnbingo/> and <https://github.com/levontumanyan/bnbingo/releases>, or with `uv tool install bnbingo && bnbingo --help`.
