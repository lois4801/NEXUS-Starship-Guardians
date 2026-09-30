# Guardian Intelligence Lab

The Guardian Intelligence Lab is the controlled evaluation layer for Nexus Starship Guardians. Its purpose is to test whether a candidate model, prompt, routing strategy, team size, repair strategy, or memory policy is actually better than the current baseline.

## Principles

- Use a fixed evaluation corpus for baseline/candidate comparisons.
- Preserve provenance for every task.
- Separate deterministic evidence from semantic judging.
- Block critical regressions even when aggregate scores improve.
- Treat cost and latency as optimization dimensions, not substitutes for correctness.
- Never auto-promote model weights merely because production traces look successful.

## Core modules

- `nexus_os.evaluation_lab.GuardianIntelligenceLab`
- `nexus_os.multi_judge.MultiJudgeReport`
- `nexus_os.promotion_gate.decide_promotion`
- `nexus_os.failure_taxonomy.classify_failure`
- `nexus_os.regression_corpus.RegressionCorpus`
- `nexus_os.strategy_tournament.StrategyTournament`

## Evaluation record

Each evaluation case should include:

- stable case ID;
- task;
- expected behavior;
- whether it is critical;
- provenance;
- tags for subsystem, language, project, or failure class.

Each outcome captures pass/fail, score, output/critique, cost, latency, and failure classification.

## Promotion gate

A candidate can be blocked when it:

- falls below the configured minimum pass rate;
- has a lower pass rate than baseline;
- misses the required score improvement;
- introduces a critical regression;
- exceeds configured cost or latency ratios.

The gate produces eligibility evidence. Consequential releases and model promotions remain subject to project approval policy.

## Strategy tournament

The tournament summarizes multiple strategies evaluated against the same corpus. It favors no-critical-regression behavior first, then pass rate, score, cost, and latency. Tournament results are evidence for routing policy; they are not permission to bypass approval or safety boundaries.
