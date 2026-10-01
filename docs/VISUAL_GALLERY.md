# Nexus Starship Guardians — Visual Gallery

The repository keeps architecture and process visuals close to the code so readers can understand the system before diving into modules.

## Current State Graph

![Nexus Starship Guardians current state](assets/current-state-graph.svg)

This is the canonical top-level system map and must be updated whenever a meaningful architecture, intelligence, execution, evaluation, learning, integration, release, or packaging change alters the flow. In v0.7 it includes **Adaptive Guardian Intelligence**, the ten-role specialist intelligence wing, verified per-skill learning, Benchmark Replay, Coverage Intelligence, the Guardian Benchmark Vault feedback loop, Intelligence Fabric, Guardian Intelligence Lab, adaptive routing, verified execution, and release/package outputs. The editable companion is [`CURRENT_STATE.md`](CURRENT_STATE.md).

## Adaptive Guardian Intelligence

![Adaptive Guardian Intelligence](assets/adaptive-guardian-intelligence.svg)

This animated graph shows how AI Architect, Software Platform Engineer, AI Developer, Coder Specialist, AI Engineer, Debugger Specialist, AI Scientist, AI Cloud Specialist, API Specialist, and AI Programmer Guardians orbit the adaptive intelligence core. Verified outcomes update per-skill quality, reliability, benchmark evidence, confidence, trend, and regression pressure. Benchmark Replay and Coverage Intelligence generate targeted learning priorities that can influence future routing without granting new permissions. See [`ADAPTIVE_GUARDIAN_INTELLIGENCE.md`](ADAPTIVE_GUARDIAN_INTELLIGENCE.md).

## Guardian Benchmark Vault

![Guardian Benchmark Vault](assets/guardian-benchmark-vault.svg)

This animated graph shows the governed learning path from verified failure to Regression Corpus, evidence-linked benchmark nomination, explicit review, versioned frozen snapshot, Guardian Intelligence Lab evaluation, Promotion Gate, and release. In v0.7, candidate replay can add reproducibility evidence before review. Rejected candidates remain review history and never enter permanent benchmark truth. See [`GUARDIAN_BENCHMARK_VAULT.md`](GUARDIAN_BENCHMARK_VAULT.md).

## Intelligence Fabric

![Nexus Intelligence Fabric](assets/intelligence-fabric.svg)

This animated visual shows the intelligence loop connecting project knowledge, strategy selection, memory quality, model-performance evidence, adversarial guardrails, uncertainty, mission intelligence, adaptive routing, verified execution, and learning. See [`INTELLIGENCE_FABRIC.md`](INTELLIGENCE_FABRIC.md).

## Project hero

![Nexus Starship Guardians hero](assets/nexus-starship-guardians-hero.svg)

## Mission intelligence and adaptive routing

![Mission intelligence and adaptive routing](assets/mission-routing-pipeline.svg)

This focused animated flow shows the path from mission text through classification, capability mapping, permission-safe Guardian routing, alternate-model judging, correlated telemetry, and cross-project learning. The canonical current-state graphic supersedes this focused diagram when architecture details differ.

## Production verification motion graph

![Production verification pipeline](assets/production-verification-pipeline.svg)

## Core architecture

The source-of-truth system flow is maintained in [`CURRENT_STATE.md`](CURRENT_STATE.md), [`ADAPTIVE_GUARDIAN_INTELLIGENCE.md`](ADAPTIVE_GUARDIAN_INTELLIGENCE.md), [`INTELLIGENCE_FABRIC.md`](INTELLIGENCE_FABRIC.md), [`GUARDIAN_BENCHMARK_VAULT.md`](GUARDIAN_BENCHMARK_VAULT.md), and [`ARCHITECTURE_VISUALS.md`](ARCHITECTURE_VISUALS.md). Mermaid diagrams stay editable while the animated SVGs provide an engaging GitHub-facing view.

## Process workflows

Feature delivery, verification, repair, specialist learning, benchmark replay, coverage analysis, benchmark nomination/review, and promotion workflows are maintained in [`PROCESS_WORKFLOWS.md`](PROCESS_WORKFLOWS.md).

## Visual design language

Nexus Starship Guardians visuals intentionally use a consistent command-center language:

- deep navy/space backgrounds;
- cyan for routing and verified execution;
- violet for reasoning, specialist intelligence, benchmark governance, and evaluation;
- amber for planning, caution and recovery;
- green for successful promotion/release;
- red/pink for verified failure or rejected paths;
- animated signal paths for system flow;
- compact engineering labels rather than decorative-only diagrams.

Visuals are documentation. When behavior changes, the corresponding graph should change in the same pull request.
