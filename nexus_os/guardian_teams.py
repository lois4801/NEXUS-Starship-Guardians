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


ELITE_SPECIALIST_GUARDIANS: tuple[GuardianRole, ...] = (
    GuardianRole(
        "AI Architect Guardian",
        "adaptive-specialists",
        "Design AI and software architectures, learn from verified tradeoffs, and reduce system-level risk.",
    ),
    GuardianRole(
        "Software Platform Engineer Guardian",
        "adaptive-specialists",
        "Build reliable multi-tenant platforms, distributed runtimes, observability, and deployment foundations.",
    ),
    GuardianRole(
        "AI Developer Guardian",
        "adaptive-specialists",
        "Build model-powered applications, RAG, Guardian workflows, and model integrations with evaluated behavior.",
    ),
    GuardianRole(
        "Coder Specialist Guardian",
        "adaptive-specialists",
        "Produce maintainable implementation code and continuously learn repository-specific patterns from tests.",
    ),
    GuardianRole(
        "AI Engineer Guardian",
        "adaptive-specialists",
        "Engineer production AI inference, routing, evaluation, reliability, latency, and quality systems.",
    ),
    GuardianRole(
        "Debugger Specialist Guardian",
        "adaptive-specialists",
        "Learn recurring failure signatures, isolate root causes, and shorten verified repair loops.",
    ),
    GuardianRole(
        "AI Scientist Guardian",
        "adaptive-specialists",
        "Design reproducible experiments, benchmarks, evaluations, and statistically grounded AI improvements.",
    ),
    GuardianRole(
        "AI Cloud Specialist Guardian",
        "adaptive-specialists",
        "Optimize cloud, containers, scaling, networking, rollback, security, observability, and cost evidence.",
    ),
    GuardianRole(
        "API Specialist Guardian",
        "adaptive-specialists",
        "Design and verify API contracts, authentication, compatibility, retries, rate limits, and integrations.",
    ),
    GuardianRole(
        "AI Programmer Guardian",
        "adaptive-specialists",
        "Solve implementation and automation problems using verified code, tools, algorithms, and replay evidence.",
    ),
)


AUTONOMOUS_OPERATIONS_GUARDIANS: tuple[GuardianRole, ...] = (
    GuardianRole(
        "Planner Strategist Guardian",
        "autonomous-operations",
        "Decompose goals into dependency-aware plans with explicit decision rules, success criteria, and trade-offs.",
    ),
    GuardianRole(
        "Verification & QA Specialist Guardian",
        "autonomous-operations",
        "Run independent verification and quality audits, capturing tool-produced evidence and bounded self-heal repairs.",
    ),
    GuardianRole(
        "Independent Reviewer Guardian",
        "autonomous-operations",
        "Review change sets against the goal and verification evidence, holding approval gates without implementation authority.",
    ),
    GuardianRole(
        "Deployment & Release Guardian",
        "autonomous-operations",
        "Prepare preview environments, guard staged promotion and release gates, and plan rollbacks from release evidence.",
    ),
    GuardianRole(
        "Evidence & Research Guardian",
        "autonomous-operations",
        "Ground claims in provenance-carrying research with evidence scores and source verification before building.",
    ),
    GuardianRole(
        "Content & SEO Strategist Guardian",
        "autonomous-operations",
        "Architect structured content, keyword intent, and conversion copy without unverifiable invented claims.",
    ),
    GuardianRole(
        "Design Experience Guardian",
        "autonomous-operations",
        "Own design systems, style universes, motion design, accessibility, and design QA audits.",
    ),
    GuardianRole(
        "Budget & Cost Controller Guardian",
        "autonomous-operations",
        "Enforce resource budgets, model routing, and failure-taxonomy accounting to lower cost per verified mission.",
    ),
    GuardianRole(
        "Data & SQL Analyst Guardian",
        "autonomous-operations",
        "Run SQL and ETL analysis with data-quality checks, dashboard verification, and BI reporting evidence.",
    ),
    GuardianRole(
        "Evaluation Judge Guardian",
        "autonomous-operations",
        "Grade outputs and trajectories against ground truth with calibrated LLM-as-judge evaluation.",
    ),
)


def artificial_architecture_team() -> tuple[GuardianRole, ...]:
    """Return the canonical 30-Guardian Artificial Architecture team."""
    return ARTIFICIAL_ARCHITECTURE_GUARDIANS


def elite_specialist_team() -> tuple[GuardianRole, ...]:
    """Return the 10-role adaptive specialist intelligence wing introduced in v0.7.0."""
    return ELITE_SPECIALIST_GUARDIANS


def autonomous_operations_team() -> tuple[GuardianRole, ...]:
    """Return the 10-role Autonomous Operations Wing acquired in v0.9.0."""
    return AUTONOMOUS_OPERATIONS_GUARDIANS


AGENCY_SERVICES_GUARDIANS: tuple[GuardianRole, ...] = (
    GuardianRole(
        "GIS & Spatial Analyst Guardian",
        "agency-services",
        "Analyze geospatial data, spatial pipelines, and map rendering with projection-safe, evidence-carrying QA.",
    ),
    GuardianRole(
        "Sales Pipeline Strategist Guardian",
        "agency-services",
        "Audit pipeline stages, deal qualification, and proposals against close and win/loss evidence.",
    ),
    GuardianRole(
        "Game Design Guardian",
        "agency-services",
        "Evaluate game loops, level pacing, narrative, economy balance, and audio/art pipelines from playtest evidence.",
    ),
    GuardianRole(
        "XR & Spatial Computing Guardian",
        "agency-services",
        "Review immersive-app architecture, spatial anchors, and 3D interaction patterns with device-profile evidence.",
    ),
    GuardianRole(
        "Paid Media Strategist Guardian",
        "agency-services",
        "Audit paid media campaigns, bidding, tracking, and attribution with platform-report evidence.",
    ),
    GuardianRole(
        "Financial Analysis Guardian",
        "agency-services",
        "Review financial models, forecasts, and reconciliations with recalculated-output evidence.",
    ),
    GuardianRole(
        "Healthcare Evidence Guardian",
        "agency-services",
        "Appraise clinical evidence, health-system workflows, and medical compliance with documented citations.",
    ),
    GuardianRole(
        "Blockchain Engineer Guardian",
        "agency-services",
        "Audit smart contracts, token mechanics, and protocol integrations with testnet and static-analysis evidence.",
    ),
    GuardianRole(
        "Embedded & IoT Guardian",
        "agency-services",
        "Review firmware, device protocols, and edge pipelines with build-log and device-trace evidence.",
    ),
    GuardianRole(
        "Knowledge & Search Guardian",
        "agency-services",
        "Evaluate retrieval pipelines, graph schemas, and ranking signals with relevance-judgment evidence.",
    ),
    GuardianRole(
        "Legal & Compliance Guardian",
        "agency-services",
        "Review contracts, compliance controls, and privacy handling with clause-citation evidence.",
    ),
    GuardianRole(
        "PMO Operations Guardian",
        "agency-services",
        "Audit project plans, meeting cadences, and status-report pipelines with plan-drift evidence.",
    ),
)


def agency_services_team() -> tuple[GuardianRole, ...]:
    """Return the 12-role Agency Services Wing acquired in v0.9.0."""
    return AGENCY_SERVICES_GUARDIANS
