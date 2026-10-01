# Nexus Starship Guardians — Releases and Packages

Nexus Starship Guardians treats releases and packages as part of the engineering evidence chain.

## Release channels

### GitHub Releases

Each stable version creates a GitHub Release containing:

- generated release notes;
- source archive from GitHub;
- Python wheel (`.whl`);
- Python source distribution (`.tar.gz`).

Stable releases use semantic tags such as `v0.3.0`, `v0.4.0`, and eventually `v1.0.0`.

### GitHub Packages / GHCR

Each stable version publishes a Docker image to GitHub Container Registry:

```text
ghcr.io/lois4801/nexus-starship-guardians:<version>
ghcr.io/lois4801/nexus-starship-guardians:<major>.<minor>
ghcr.io/lois4801/nexus-starship-guardians:latest
```

The image is built from the repository `Dockerfile` and is subject to the same Docker health verification used in CI.

## Release history

### v0.3.0 — first formal Starship Guardians release

Published and verified through GitHub Actions. It established:

- Guardian Intelligence Lab, multi-judge evaluation, regression corpus, and promotion gates;
- adaptive Guardian routing and persistent performance evidence;
- PostgreSQL distributed queue foundation;
- Python 3.11/3.12/3.13, live Uvicorn, Docker, and PostgreSQL production-verification gates;
- Mission Intelligence primitives;
- reconciled ChatGPT/Codex plugin;
- canonical Current State Graph;
- automated GitHub Release + GHCR package publication.

### v0.4.0 — live Mission Runtime and controlled integration policy

Current release target. It adds:

- live Mission Intelligence in the REST run path;
- project-scoped mission planning endpoint;
- collective multi-Guardian capability/tool coverage;
- controlled high-level Tool Gateway policy;
- separate project `gateway_tools` permissions;
- Lucio AI Platform, Ember, Nexus Code, Railway, and Supabase readiness contracts;
- integration-readiness API that never equates readiness with a real connection;
- durable `mission_intelligence` events in run traces;
- updated Current State Graph and v0.4 ChatGPT/Codex plugin metadata.

## Release process

1. Implement on a feature/release branch.
2. Update the Current State Graph if architecture changed.
3. Update tests, docs, learnings, and changelog.
4. Bump `pyproject.toml` to a stable semantic version.
5. Keep both plugin manifests aligned when the plugin changes.
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

**v0.4.0** — Live Mission Runtime, collective Guardian routing, controlled tool-gateway policy, and explicit external-integration readiness contracts while preserving REST v1 compatibility.
