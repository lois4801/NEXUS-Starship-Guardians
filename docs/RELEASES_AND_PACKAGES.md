# Nexus Starship Guardians — Releases and Packages

Nexus Starship Guardians treats releases and packages as part of the engineering evidence chain.

## Release channels

### GitHub Releases

Each stable version should create a GitHub Release containing:

- generated release notes;
- source archive from GitHub;
- Python wheel (`.whl`);
- Python source distribution (`.tar.gz`).

Stable releases use semantic tags such as `v0.3.0`, `v0.4.0`, and eventually `v1.0.0`.

### GitHub Packages / GHCR

Each stable version should publish a Docker image to GitHub Container Registry:

```text
ghcr.io/lois4801/nexus-starship-guardians:<version>
ghcr.io/lois4801/nexus-starship-guardians:<major>.<minor>
ghcr.io/lois4801/nexus-starship-guardians:latest
```

The image is built from the repository `Dockerfile` and is subject to the same Docker health verification used in CI.

## Release process

1. Implement on a feature/release branch.
2. Update the Current State Graph if architecture changed.
3. Update tests, docs, learnings, and changelog.
4. Bump `pyproject.toml` to a stable semantic version.
5. Keep the plugin manifest version aligned when the plugin changes.
6. Open a pull request and require the normal CI matrix to pass.
7. Merge into protected `main`.
8. Release automation validates metadata, builds Python distributions, creates the version tag and GitHub Release, and publishes the GHCR image.
9. Verify the new entry appears under both **Releases** and **Packages** on GitHub.

## Versioning policy

- `0.x.y`: active pre-1.0 development with compatibility preservation where practical.
- patch (`x.y.Z`): bug fixes, compatibility, documentation, verification improvements.
- minor (`x.Y.0`): new subsystems, major routing/evaluation/integration capabilities.
- major (`X.0.0`): deliberately versioned breaking changes.

Technical legacy identifiers such as the `nexus_os` Python namespace and REST v1 `agent` / `agents` fields are not removed merely because the product name changed. Their removal requires a documented migration and regression coverage.

## Current release target

**v0.3.0** is the first formal Nexus Starship Guardians release target after the product rename, plugin reconciliation, production-verification matrix, Mission Intelligence, Guardian Intelligence Lab, adaptive routing, learning/regression infrastructure, and PostgreSQL distributed queue foundation.
