# Guardian Cognitive Evolution — v0.8.0

Guardian Cognitive Evolution is the meta-learning layer above Adaptive Guardian Intelligence. It is designed to make specialist Guardians improve from verified work without pretending that hosted model weights rewrite themselves after every request.

## Cognitive loop

```text
mission
  ↓
specialist Guardian executes
  ↓
objective verification
  ↓
per-skill adaptive evidence
  ↓
cognitive episode
  ├─ reusable lesson
  ├─ confidence calibration
  ├─ failure signature / cluster
  ├─ counterfactual replay plan
  └─ self-training curriculum
  ↓
bounded adaptive + cognitive routing
  ↓
next mission
```

## Ten evolving specialists

The live specialist wing remains:

1. AI Architect Guardian
2. Software Platform Engineer Guardian
3. AI Developer Guardian
4. Coder Specialist Guardian
5. AI Engineer Guardian
6. Debugger Specialist Guardian
7. AI Scientist Guardian
8. AI Cloud Specialist Guardian
9. API Specialist Guardian
10. AI Programmer Guardian

## What v0.8 adds

### Verified cross-Guardian knowledge transfer

A specialist may publish a reusable `CognitiveLesson` after a verified episode. Another specialist can retrieve the lesson when its skills overlap with the new mission.

Knowledge transfer does **not** copy performance scores. The receiving Guardian must still prove the skill itself before its adaptive competence or routing evidence improves.

### Confidence calibration

When mission confidence is available, the cognitive engine compares predicted confidence with the verified outcome using a Brier-style calibration signal. Repeated overconfidence can reduce the small cognitive routing bonus; well-calibrated evidence can improve it within strict bounds.

### Failure intelligence

Verified failures are grouped into persistent failure clusters by signature. This surfaces recurring failure modes across specialists instead of treating every incident as isolated.

### Counterfactual replay

Failures automatically create alternate-strategy plans. Depending on the failure domain, plans may include:

- minimal reproduction;
- hypothesis-first debugging;
- binary isolation;
- threat-model-first review;
- adversarial testing;
- schema-diff-first migration review;
- transactional rehearsal;
- contract-first API validation;
- failure injection;
- staged rollout;
- rollback simulation;
- constraint-first architecture;
- tradeoff matrices;
- independent review.

These are replay candidates, not automatic claims that an alternate strategy would have succeeded.

### Self-curriculum

Each specialist can generate a curriculum from:

- weak adaptive skill scores;
- low confidence / insufficient evidence;
- declining trends;
- critical regressions;
- recurring failure clusters;
- relevant peer lessons.

Exercises require replay, adversarial review, and evidence-backed teach-back rather than passive text memorization.

## Routing

Routing now combines three distinct signals:

```text
registry utility
+ bounded direct skill-evidence bonus
+ smaller bounded cognitive-calibration bonus
```

The cognitive contribution is deliberately smaller than direct verified skill evidence. Meta-learning can refine selection but cannot overwhelm demonstrated competence.

## Live API

`GET /v1/projects/{project_id}/guardians/{guardian_id}/cognitive-summary`

returns the Guardian's adaptive summary plus:

- verified cognitive episodes;
- authored lessons;
- counterfactual cycle count;
- confidence reliability;
- recent lessons;
- current curriculum.

The endpoint is project-authenticated but the specialist intelligence itself remains runtime-wide evidence.

## Safety and governance invariants

Cognitive Evolution may automatically change:

- persistent lessons;
- confidence calibration;
- failure clusters;
- replay strategies;
- self-curricula;
- a small bounded routing preference.

It may **not** automatically:

- grant filesystem, GitHub, browser, API, database, cloud, deployment, or model permissions;
- copy another Guardian's competence score;
- mutate hosted model weights in production;
- accept self-reported success as verification;
- approve Benchmark Vault truth;
- overwrite the frozen benchmark corpus;
- bypass promotion or release gates.

## Practical meaning of “super-Guardian”

In Nexus, a super-Guardian is not an uncontrolled self-modifying model. It is a specialist whose decisions compound from verified experience: it remembers what worked, recognizes recurring failure patterns, becomes better calibrated about uncertainty, tests alternate strategies after failures, learns relevant lessons from peers, practices its weakest capabilities, and lets that evidence influence future routing within explicit governance boundaries.
