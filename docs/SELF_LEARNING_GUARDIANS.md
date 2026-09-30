# Nexus Starship Guardians — Self-Learning and Verified Repair

## Definition

In Nexus Starship Guardians, **self-learning** means improvement across missions through:

1. episodic memory of missions, critiques, scores, and evidence;
2. reflection that distills reusable lessons;
3. retrieval of relevant prior lessons into future Guardian prompts;
4. evaluation and regression suites that grow from failures;
5. optional offline SFT/LoRA preparation from curated high-scoring episodes.

It does **not** mean changing model weights live in production. Weight updates are a separate offline pipeline and must beat the current baseline before promotion.

## 30-Guardian Artificial Architecture team

The canonical architecture team is defined in `nexus_os.guardian_teams` and contains 30 unique Guardians across command, learning, code quality, source control, verification, execution, repair, and operations.

## Automatic learning cycle

```text
MISSION
  -> retrieve relevant prior lessons
  -> Guardian swarm
  -> lead synthesis
  -> verification/evaluation
  -> if failing: bounded repair loop
  -> Reflection Guardian distills reusable lesson
  -> store episode + critique + evidence + lesson
  -> next mission retrieves relevant lessons
```

The portable `swarm` command performs this memory/reflection cycle automatically. Set `NEXUS_LEARNING_PATH` to move the append-only JSONL learning store; the default is `.nexus/guardian_learning.jsonl`.

## Verified repair

`VerifiedAutoRepairLoop` implements a bounded build -> verify -> repair cycle. The default architecture should cap repair rounds at three. Every verification result is added to an `EvidenceBundle`, and the final run can be written to the Guardian learning store.

A repair is not considered successful merely because a coding Guardian says it is fixed. The configured verifier must pass.

## Automatic diff review

`AutomaticDiffReviewer` performs deterministic first-pass checks before model or human review. Current checks include:

- unresolved merge-conflict markers;
- possible credentials/private keys;
- TLS verification disablement;
- new TODO/FIXME/HACK markers;
- unjustified lint suppressions;
- oversized diffs that should be split or receive focused review.

High-severity findings are blocking.

## Git conflict/rebase handling

`GitConflictManager` uses argv-based Git calls only. It can rebase an isolated worktree, enumerate conflicted files, and abort safely. It intentionally does not blindly auto-resolve conflicts. A repair Guardian can use the conflict evidence to propose structured edits, after which the branch must be re-tested.

## Browser and API verification

`APITestWorker` performs bounded checks against one configured HTTP(S) origin. Paths must be origin-relative.

`BrowserTestWorker` runs an operator-configured browser suite through the existing restricted local process worker, inheriting executable allowlists, workspace containment, timeouts, and output limits.

## Durable resumable jobs

`SqliteJobQueue` persists Guardian work across process restarts. It supports:

- FIFO claiming;
- bounded attempts;
- retry after failure;
- terminal failed state after retry exhaustion;
- recovery of interrupted `running` jobs back to `pending` after a restart.

For distributed production deployment, migrate this interface to PostgreSQL/Redis/queue infrastructure while preserving the same state semantics.

## Evidence bundles

`EvidenceBundle` stores provenance-tracked text evidence with SHA-256 digests. Verification, diff review, test output, repair reflection, and release evidence can be attached to one mission bundle. The digest detects accidental or unauthorized evidence mutation after capture.

## Offline improvement pipeline

`JsonlLearningStore.export_sft_pairs()` exports high-scoring mission pairs for later curation. Do not automatically fine-tune or promote a model from raw production traces. Recommended promotion flow:

```text
high-scoring verified episodes
  -> redact secrets/private data
  -> human/quality curation
  -> offline SFT/LoRA
  -> fixed evaluation suite
  -> compare against current baseline
  -> promote only if better and safe
```

## Operating rule

Optimize for **verified successful missions**, not raw Guardian count or token volume. A 30-Guardian or 200-Guardian mission is useful only when the work can be decomposed and independently verified.
