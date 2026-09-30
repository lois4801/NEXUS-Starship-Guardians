from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GuardianRole:
    name: str
    division: str
    mission: str


ARTIFICIAL_ARCHITECTURE_GUARDIANS: tuple[GuardianRole, ...] = (
    GuardianRole("Chief Guardian Architect", "command", "Own system architecture and final technical synthesis."),
    GuardianRole("Mission Planner Guardian", "command", "Decompose goals into dependency-aware work."),
    GuardianRole("Reality Check Guardian", "command", "Challenge unsupported completion claims and assumptions."),
    GuardianRole("Evidence Guardian", "command", "Require provenance and evidence for important outcomes."),
    GuardianRole("Learning Architect Guardian", "learning", "Design episodic memory, reflection, and lesson retrieval."),
    GuardianRole("Evaluation Guardian", "learning", "Design repeatable quality and regression evaluations."),
    GuardianRole("Reflection Guardian", "learning", "Distill reusable lessons from critiques and outcomes."),
    GuardianRole("Fine-Tuning Curator Guardian", "learning", "Curate offline training candidates without live weight mutation."),
    GuardianRole("Diff Intelligence Guardian", "code-quality", "Inspect code diffs for risk, defects, and scope creep."),
    GuardianRole("Code Review Guardian", "code-quality", "Review implementation correctness and maintainability."),
    GuardianRole("Security Review Guardian", "code-quality", "Detect credential, auth, dependency, and unsafe execution risks."),
    GuardianRole("Performance Guardian", "code-quality", "Check performance regressions and resource pressure."),
    GuardianRole("Git Worktree Guardian", "source-control", "Maintain isolated task branches and worktrees."),
    GuardianRole("Conflict Recovery Guardian", "source-control", "Detect and safely recover from rebase and merge conflicts."),
    GuardianRole("Integration Guardian", "source-control", "Order verified changes for integration."),
    GuardianRole("Release Guardian", "source-control", "Guard release readiness and approval gates."),
    GuardianRole("API Test Guardian", "verification", "Run bounded API contract and regression checks."),
    GuardianRole("Browser Test Guardian", "verification", "Run browser and end-to-end workflow verification."),
    GuardianRole("Unit Test Guardian", "verification", "Generate and execute focused unit tests."),
    GuardianRole("Regression Guardian", "verification", "Grow regression coverage from prior failures."),
    GuardianRole("Queue Reliability Guardian", "execution", "Own resumable durable work and retry policy."),
    GuardianRole("Sandbox Guardian", "execution", "Enforce execution isolation and command allowlists."),
    GuardianRole("Filesystem Guardian", "execution", "Apply scoped structured file edits safely."),
    GuardianRole("Tool Policy Guardian", "execution", "Control tool permissions and consequential action gates."),
    GuardianRole("Repair Planner Guardian", "repair", "Convert failed verification into bounded repair tasks."),
    GuardianRole("Repair Builder Guardian", "repair", "Produce targeted fixes from verified failure evidence."),
    GuardianRole("Repair Verifier Guardian", "repair", "Re-run checks after every repair attempt."),
    GuardianRole("Failure Taxonomy Guardian", "repair", "Classify recurring failures for future prevention."),
    GuardianRole("Observability Guardian", "operations", "Track runs, latency, failure rates, and evidence."),
    GuardianRole("Cost Efficiency Guardian", "operations", "Optimize cost per successful verified mission."),
)


def artificial_architecture_team() -> tuple[GuardianRole, ...]:
    """Return the canonical 30-Guardian Artificial Architecture team."""
    return ARTIFICIAL_ARCHITECTURE_GUARDIANS
