# Nexus Starship Guardians — Visual Gallery

The repository keeps architecture and process visuals close to the code so readers can understand the system before diving into modules.

## Current State Graph

![Nexus Starship Guardians current state](assets/current-state-graph.svg)

This is the canonical top-level system map and must be updated whenever a meaningful architecture, execution, evaluation, learning, integration, release, or packaging change alters the flow. The editable companion is [`CURRENT_STATE.md`](CURRENT_STATE.md).

## Project hero

![Nexus Starship Guardians hero](assets/nexus-starship-guardians-hero.svg)

## Mission intelligence and adaptive routing

![Mission intelligence and adaptive routing](assets/mission-routing-pipeline.svg)

This animated flow shows the path from mission text through classification, capability mapping, permission-safe Guardian routing, alternate-model judging, correlated telemetry, and cross-project learning.

## Production verification motion graph

![Production verification pipeline](assets/production-verification-pipeline.svg)

## Core architecture

The source-of-truth system flow is maintained in [`CURRENT_STATE.md`](CURRENT_STATE.md) and [`ARCHITECTURE_VISUALS.md`](ARCHITECTURE_VISUALS.md). Mermaid diagrams stay editable while the animated SVGs provide an engaging GitHub-facing view.

## Process workflows

Feature delivery, verification, repair, learning, and promotion workflows are maintained in [`PROCESS_WORKFLOWS.md`](PROCESS_WORKFLOWS.md).

## Visual design language

Nexus Starship Guardians visuals intentionally use a consistent command-center language:

- deep navy/space backgrounds;
- cyan for routing and verified execution;
- violet for reasoning/evaluation;
- amber for planning, caution and recovery;
- green for successful promotion/release;
- animated signal paths for system flow;
- compact engineering labels rather than decorative-only diagrams.

Visuals are documentation. When behavior changes, the corresponding graph should change in the same pull request.
