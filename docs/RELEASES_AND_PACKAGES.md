# Nexus Starship Guardians — Releases and Packages

Nexus Starship Guardians treats releases and packages as part of the engineering evidence chain.

## Release channels

### GitHub Releases

Each stable version creates a GitHub Release containing:

- generated release notes;
- source archive from GitHub;
- Python wheel (`.whl`);
- Python source distribution (`.tar.gz`).

Stable releases use semantic tags such as `v0.3.0`, `v0.4.0`, `v0.5.0`, and eventually `v1.0.0`.

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

Published and verified through GitHub Actions. It established Guardian Intelligence Lab, multi-judge evaluation, regression protection, adaptive routing, distributed queue foundations, production-verification gates, the reconciled plugin, Current State Graph, and automated release/package publication.

### v0.4.0 — live Mission Runtime and controlled integration policy

Published and verified through GitHub Actions. It added live Mission Intelligence, project-scoped mission planning, collective Guardian routing, controlled high-level Tool Gateway policy, integration-readiness contracts, and durable `mission_intelligence` evidence.

### v0.5.0 — Intelligence Fabric

Current release target. It adds:

- `IntelligenceFabric` composition layer;
- explicit Strategy Engine with inspectable strategy rationale and evidence requirements;
- Knowledge Graph foundation with dependency/impact traversal;
- Model Performance Registry using verified task-specific quality/reliability/cost/latency evidence;
- Memory Quality Registry with helpful/harmful/neutral reuse tracking and quarantine;
- deterministic adversarial guardrail generation;
- explicit uncertainty and assumptions;
- project-scoped `/intelligence-plan` API;
- durable `strategy_intelligence` run evidence;
- updated animated Current State Graph and dedicated Intelligence Fabric visual;
- runtime/plugin release alignment at `0.5.0`.

## Release process

1. Implement on a feature/release branch.
2. Update the Current State Graph if architecture changed.
3. Update tests, docs, visuals, learnings, and changelog.
4. Bump `pyproject.toml` to a stable semantic version.
5. Keep both plugin manifests aligned when the plugin changes.
6. Open a pull request and require the normal CI matrix to pass.
7. Merge into protected `main`.
8. Release automation validates metadata, builds Python distributions, creates the version tag and GitHub Release, and publishes the GHCR image.
9. Verify the new entry appears under both **Releases** and **Packages** on GitHub.

## Versioning policy

- `0.x.y`: active pre-1.0 development with compatibility preservation where practical.
- patch (`x.y.Z`): bug fixes, compatibility, documentation, verification improvements.
- minor (`x.Y.0`): new subsystems, major routing/evaluation/integration/intelligence capabilities.
- major (`X.0.0`): deliberately versioned breaking changes.

Technical legacy identifiers such as the `nexus_os` Python namespace and REST v1 `agent` / `agents` fields are not removed merely because the product name changed. Their removal requires a documented migration and regression coverage.

## Current release target

**v0.5.0** — Nexus Intelligence Fabric: strategy selection, Knowledge Graph foundations, memory-quality controls, task-specific model-performance evidence, adversarial guardrails, uncertainty, and durable strategy intelligence while preserving v0.4 compatibility.
