# Nexus Starship Guardians — Process Workflows

## Feature development workflow

```mermaid
flowchart TD
    A[Mission Received] --> B[Classify Mission]
    B --> C[Build Capability Requirements]
    C --> D[Select Guardian Team]
    D --> E[Plan Dependency DAG]
    E --> F[Create Isolated Worktrees]
    F --> G[Parallel Build]
    G --> H[Automatic Diff Review]
    H --> I[Verification Grid]
    I --> J{All required checks pass?}
    J -->|No| K[Verified Repair Loop]
    K --> I
    J -->|Yes| L[Evidence Bundle]
    L --> M[Multi-Judge Evaluation]
    M --> N{Promotion Gate}
    N -->|Block| O[Failure Taxonomy + Regression Case]
    O --> D
    N -->|Eligible| P[Human / Policy Approval]
    P --> Q[PR / Release]
```

## Failure-to-learning workflow

```mermaid
flowchart TD
    A[Verification Failure] --> B[Classify Failure]
    B --> C[Capture Evidence]
    C --> D[Repair Guardian]
    D --> E[Re-verify]
    E --> F{Fixed?}
    F -->|No| G[Bounded Retry]
    G --> D
    F -->|Yes| H[Create / Deduplicate Regression Case]
    H --> I[Reflection Guardian]
    I --> J[Learning Memory]
    J --> K[Future Mission Retrieval]
```

## Model / prompt / strategy promotion workflow

```mermaid
flowchart LR
    A[Fixed Evaluation Corpus] --> B[Current Baseline]
    A --> C[Candidate]
    B --> D[Run Multi-Judge Suite]
    C --> E[Run Multi-Judge Suite]
    D --> F[Baseline Summary]
    E --> G[Candidate Summary]
    F --> H[Promotion Gate]
    G --> H
    H -->|No critical regression + policy met| I[Eligible for Approval]
    H -->|Regression / insufficient gain| J[Blocked]
    J --> K[Failure Analysis]
    K --> L[Improve Candidate]
```

## Distributed Guardian job lifecycle

```mermaid
stateDiagram-v2
    [*] --> pending
    pending --> running: worker claims with lease
    running --> running: heartbeat renews lease
    running --> completed: verified success
    running --> pending: retryable failure
    running --> pending: expired lease recovered
    running --> failed: attempts exhausted
    pending --> failed: attempts exhausted
    completed --> [*]
    failed --> [*]
```

## Required evidence for a change

A repository change is considered documented when it includes, where applicable:

1. implementation code;
2. automated tests;
3. architecture/process visual updates;
4. verification evidence or CI status;
5. a learning/retrospective entry describing failures, fixes, and reusable lessons.
