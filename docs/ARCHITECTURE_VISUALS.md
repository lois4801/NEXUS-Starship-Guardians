# Nexus Starship Guardians — Architecture Visuals

These Mermaid diagrams are the canonical GitHub-viewable visual architecture for Nexus Starship Guardians. Update them whenever a meaningful execution, learning, routing, or deployment change is made.

## End-to-end architecture

```mermaid
flowchart TD
    A[Nexus Starship Guardians] --> B[Mission Command]
    B --> C[Mission Classifier]
    C --> D[Capability Map]
    D --> E[Guardian Registry]
    E --> F[Adaptive Router]

    F --> G[Models]
    F --> H[Guardians]
    F --> I[Tools]

    G --> J[Execution Planner]
    H --> J
    I --> J

    J --> K[Dependency-Aware DAG]
    K --> L[Isolated Git Worktrees]
    L --> M[Parallel Build Guardians]
    M --> N[Automatic Diff Review]
    N --> O[Verification Grid]

    O --> P[API Tests]
    O --> Q[Browser Tests]
    O --> R[Unit / Integration Tests]

    P --> S[Verified Auto Repair]
    Q --> S
    R --> S

    S --> T[Evidence Bundle]
    T --> U[Multi-Judge Evaluation]
    U --> V[Failure Taxonomy]
    V --> W[Regression Corpus]
    W --> X[Learning Memory]
    X --> Y[Strategy Tournament]
    Y --> Z[Promotion Gate]
    Z --> AA[Release]
```

## Guardian Intelligence loop

```mermaid
flowchart LR
    A[Real + Synthetic Tasks] --> B[Baseline Strategy]
    A --> C[Candidate Strategy]
    B --> D[Deterministic Judge]
    B --> E[Evidence Judge]
    C --> F[Deterministic Judge]
    C --> G[Evidence Judge]
    D --> H[Evaluation Summary]
    E --> H
    F --> I[Evaluation Summary]
    G --> I
    H --> J[Promotion Gate]
    I --> J
    J -->|Pass| K[Eligible for Approval]
    J -->|Block| L[Failure Taxonomy]
    L --> M[Regression Corpus]
    M --> A
```

## Adaptive Guardian routing

```mermaid
flowchart TD
    A[Mission Requirements] --> B[Required Capabilities]
    A --> C[Required Tools]
    B --> D[Guardian Registry]
    C --> D
    D --> E[Historical Reliability]
    D --> F[Quality Score]
    D --> G[Cost]
    D --> H[Latency]
    E --> I[Adaptive Router]
    F --> I
    G --> I
    H --> I
    I --> J[Smallest Sufficient Guardian Team]
    J --> K[Execution Planner]
```

## Distributed execution

```mermaid
flowchart TD
    A[Mission Queue] --> B[(PostgreSQL guardian_jobs)]
    B --> C[Worker A]
    B --> D[Worker B]
    B --> E[Worker N]
    C --> F[Lease + Heartbeat]
    D --> G[Lease + Heartbeat]
    E --> H[Lease + Heartbeat]
    F --> I{Completed?}
    G --> I
    H --> I
    I -->|Yes| J[Evidence + Result]
    I -->|Retryable failure| K[Requeue]
    I -->|Attempts exhausted| L[Failed / Dead-letter handling]
    K --> B
```

## Repository update standard

Every meaningful change should leave four forms of evidence in GitHub:

```text
Code + Tests + Documentation/Visuals + Learnings/Retrospective
```

This makes architecture drift and undocumented self-learning less likely.
