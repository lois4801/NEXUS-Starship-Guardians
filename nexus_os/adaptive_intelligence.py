from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SpecialistIntelligenceProfile:
    guardian_id: str
    role: str
    capabilities: frozenset[str]
    benchmark_tags: frozenset[str]
    learning_objectives: tuple[str, ...]


@dataclass(slots=True)
class SkillEvidence:
    attempts: int = 0
    successes: int = 0
    total_score: float = 0.0
    benchmark_passes: int = 0
    benchmark_failures: int = 0
    critical_regressions: int = 0
    recent_scores: list[float] = field(default_factory=list)
    updated_at: float = 0.0

    @property
    def success_rate(self) -> float:
        return self.successes / self.attempts if self.attempts else 0.0

    @property
    def average_score(self) -> float:
        return self.total_score / self.attempts if self.attempts else 0.0

    @property
    def benchmark_rate(self) -> float:
        total = self.benchmark_passes + self.benchmark_failures
        return self.benchmark_passes / total if total else 0.5

    @property
    def confidence(self) -> float:
        return min(1.0, self.attempts / 12.0)

    @property
    def trend(self) -> float:
        if len(self.recent_scores) < 4:
            return 0.0
        midpoint = len(self.recent_scores) // 2
        earlier = self.recent_scores[:midpoint]
        later = self.recent_scores[midpoint:]
        if not earlier or not later:
            return 0.0
        return (sum(later) / len(later)) - (sum(earlier) / len(earlier))

    @property
    def adaptive_score(self) -> float:
        if not self.attempts:
            return 5.0
        quality = self.average_score
        reliability = self.success_rate * 10.0
        benchmark = self.benchmark_rate * 10.0
        regression_penalty = min(4.0, self.critical_regressions * 1.5)
        trend_bonus = max(-1.0, min(1.0, self.trend * 0.25))
        return max(
            0.0,
            min(
                10.0,
                (quality * 0.45)
                + (reliability * 0.30)
                + (benchmark * 0.25)
                - regression_penalty
                + trend_bonus,
            ),
        )


@dataclass(slots=True)
class GuardianAdaptiveState:
    guardian_id: str
    role: str
    skills: dict[str, SkillEvidence] = field(default_factory=dict)
    verified_runs: int = 0
    learning_cycles: int = 0
    last_learning_at: float = 0.0


@dataclass(frozen=True, slots=True)
class TrainingPriority:
    skill: str
    score: float
    confidence: float
    priority: float
    rationale: str


SPECIALIST_INTELLIGENCE_PROFILES: tuple[SpecialistIntelligenceProfile, ...] = (
    SpecialistIntelligenceProfile(
        guardian_id="ai-architect",
        role="AI Architect Guardian",
        capabilities=frozenset(
            {"architecture", "systems-design", "ai-architecture", "tradeoff-analysis", "integration-design"}
        ),
        benchmark_tags=frozenset({"architecture", "ai-ml", "integration", "reliability"}),
        learning_objectives=(
            "Improve architecture decisions from verified production outcomes.",
            "Reduce coupling, migration risk, and unsupported design assumptions.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="software-platform-engineer",
        role="Software Platform Engineer Guardian",
        capabilities=frozenset(
            {"platform-engineering", "distributed-systems", "reliability", "deployment", "observability"}
        ),
        benchmark_tags=frozenset({"platform", "deployment", "reliability", "cloud"}),
        learning_objectives=(
            "Improve platform reliability using deployment and runtime evidence.",
            "Learn safe scaling, queueing, tenancy, and observability patterns.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="ai-developer",
        role="AI Developer Guardian",
        capabilities=frozenset(
            {"ai-development", "rag", "agents", "model-integration", "prompt-engineering"}
        ),
        benchmark_tags=frozenset({"ai-ml", "tool-use", "integration", "coding"}),
        learning_objectives=(
            "Improve model orchestration and retrieval quality from evaluated runs.",
            "Reduce hallucination, tool misuse, and brittle prompt behavior.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="coder-specialist",
        role="Coder Specialist Guardian",
        capabilities=frozenset(
            {"coding", "refactoring", "code-review", "testing", "implementation"}
        ),
        benchmark_tags=frozenset({"coding", "testing", "regression", "engineering"}),
        learning_objectives=(
            "Increase verified implementation correctness and maintainability.",
            "Learn recurring repository patterns and avoid prior regressions.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="ai-engineer",
        role="AI Engineer Guardian",
        capabilities=frozenset(
            {"ai-engineering", "inference", "evaluation", "model-routing", "production-ai"}
        ),
        benchmark_tags=frozenset({"ai-ml", "evaluation", "reliability", "performance"}),
        learning_objectives=(
            "Improve production AI quality, latency, reliability, and evaluation discipline.",
            "Adapt model and strategy selection from benchmark evidence.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="debugger-specialist",
        role="Debugger Specialist Guardian",
        capabilities=frozenset(
            {"debugging", "root-cause-analysis", "regression-analysis", "repair", "testing"}
        ),
        benchmark_tags=frozenset({"debugging", "regression", "failure", "verification"}),
        learning_objectives=(
            "Learn failure signatures and root-cause patterns from verified incidents.",
            "Shorten repair loops while preventing repeated failures.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="ai-scientist",
        role="AI Scientist Guardian",
        capabilities=frozenset(
            {"ai-research", "experimentation", "evaluation", "statistics", "benchmark-design"}
        ),
        benchmark_tags=frozenset({"ai-ml", "evaluation", "benchmark", "research"}),
        learning_objectives=(
            "Improve experiment quality through reproducible evidence and controls.",
            "Detect weak benchmarks, confounders, and misleading aggregate metrics.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="ai-cloud-specialist",
        role="AI Cloud Specialist Guardian",
        capabilities=frozenset(
            {"cloud", "containers", "deployment", "scaling", "infrastructure", "observability"}
        ),
        benchmark_tags=frozenset({"cloud", "deployment", "security", "reliability"}),
        learning_objectives=(
            "Improve cloud deployment safety and resilience from live evidence.",
            "Learn cost, scaling, container, network, and rollback patterns.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="api-specialist",
        role="API Specialist Guardian",
        capabilities=frozenset(
            {"api-design", "contracts", "integration", "authentication", "testing"}
        ),
        benchmark_tags=frozenset({"api", "integration", "security", "tool-use"}),
        learning_objectives=(
            "Improve API contract correctness and backward compatibility.",
            "Learn authentication, retry, rate-limit, and integration failure patterns.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="ai-programmer",
        role="AI Programmer Guardian",
        capabilities=frozenset(
            {"programming", "automation", "algorithms", "tool-use", "testing"}
        ),
        benchmark_tags=frozenset({"coding", "automation", "tool-use", "engineering"}),
        learning_objectives=(
            "Improve program synthesis through verified tests and replay.",
            "Learn repository-specific implementation patterns without unsafe self-modification.",
        ),
    ),
    # --- Autonomous Operations Wing (v0.9.0) -------------------------------------
    # Specialists acquired from the Guardian fleet owner's other repositories:
    # LucioDigital-Platform (Dev Agent planner / QA / browser evidence / reviewer /
    # deployment phases), Lucio-AI-Platform (18-agent assistant squad: evidence,
    # content, SEO, design, motion, budget, CRM strategy agents), and the
    # Multi-Agent AI System (supervisor routing, SQL tool agents, human-in-the-loop
    # verification, LLM-as-judge evaluation). Anonato-Code was surveyed and excluded
    # as a source: it archives leaked proprietary source code, so no code, text, or
    # agent definitions were taken from it.
    SpecialistIntelligenceProfile(
        guardian_id="planner-strategist",
        role="Planner Strategist Guardian",
        capabilities=frozenset(
            {
                "planning",
                "goal-decomposition",
                "task-routing",
                "decision-rules",
                "prioritization",
                "success-criteria",
                "tradeoff-analysis",
            }
        ),
        benchmark_tags=frozenset({"planning", "architecture", "strategy", "reliability"}),
        learning_objectives=(
            "Improve plan quality from verified execution outcomes.",
            "State decision rules, success criteria, and trade-offs before implementation.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="verification-qa-specialist",
        role="Verification & QA Specialist Guardian",
        capabilities=frozenset(
            {
                "verification",
                "testing",
                "quality-audits",
                "browser-qa",
                "evidence-capture",
                "self-heal-repair",
            }
        ),
        benchmark_tags=frozenset({"testing", "verification", "quality", "reliability"}),
        learning_objectives=(
            "Raise verification fidelity using tool-produced evidence only.",
            "Learn failure signatures that separate real defects from flaky checks.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="reviewer-specialist",
        role="Independent Reviewer Guardian",
        capabilities=frozenset(
            {
                "code-review",
                "change-set-review",
                "approval-gates",
                "evidence-gated-approval",
                "scope-control",
            }
        ),
        benchmark_tags=frozenset({"review", "quality", "security", "compliance"}),
        learning_objectives=(
            "Strengthen independent review so approval requires verification evidence.",
            "Learn recurring defect and scope-creep patterns from reviewed change sets.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="deployment-release-specialist",
        role="Deployment & Release Guardian",
        capabilities=frozenset(
            {
                "deployment",
                "release-management",
                "preview-environments",
                "promotion-gates",
                "rollback",
            }
        ),
        benchmark_tags=frozenset({"deployment", "release", "reliability", "operations"}),
        learning_objectives=(
            "Make releases safer using preview evidence and staged promotion.",
            "Learn rollback, gating, and environment-drift patterns from release outcomes.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="evidence-research-specialist",
        role="Evidence & Research Guardian",
        capabilities=frozenset(
            {
                "research",
                "evidence-scoring",
                "provenance",
                "source-verification",
                "fact-checking",
            }
        ),
        benchmark_tags=frozenset({"research", "evidence", "quality", "analysis"}),
        learning_objectives=(
            "Ground plans and claims in provenance-carrying evidence.",
            "Learn which sources and scoring signals predict factual reliability.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="content-seo-strategist",
        role="Content & SEO Strategist Guardian",
        capabilities=frozenset(
            {
                "content-strategy",
                "copywriting",
                "seo",
                "keyword-intent",
                "conversion-psychology",
                "structured-content",
            }
        ),
        benchmark_tags=frozenset({"content", "seo", "conversion", "quality"}),
        learning_objectives=(
            "Improve content usefulness and search accuracy from measured outcomes.",
            "Learn industry-specific content patterns without inventing unverifiable claims.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="design-experience-specialist",
        role="Design Experience Guardian",
        capabilities=frozenset(
            {
                "design-systems",
                "visual-design",
                "motion-design",
                "accessibility",
                "style-systems",
                "design-qa",
            }
        ),
        benchmark_tags=frozenset({"design", "frontend", "accessibility", "quality"}),
        learning_objectives=(
            "Raise design consistency and accessibility from audit evidence.",
            "Learn which style and motion choices survive responsive and reduced-motion checks.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="budget-cost-controller",
        role="Budget & Cost Controller Guardian",
        capabilities=frozenset(
            {
                "budgeting",
                "cost-optimization",
                "model-routing",
                "resource-budgets",
                "failure-taxonomy",
            }
        ),
        benchmark_tags=frozenset({"cost", "efficiency", "reliability", "operations"}),
        learning_objectives=(
            "Lower cost per verified mission without quality loss.",
            "Learn model-routing and budget-cap patterns that prevent runaway spend.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="data-analyst-specialist",
        role="Data & SQL Analyst Guardian",
        capabilities=frozenset(
            {
                "data-analysis",
                "sql",
                "database-queries",
                "etl",
                "data-quality",
                "dashboard-verification",
                "bi-reporting",
            }
        ),
        benchmark_tags=frozenset({"data", "sql", "quality", "analysis"}),
        learning_objectives=(
            "Improve query correctness and data-quality judgments from verified results.",
            "Learn ETL, wrangling, and dashboard-verification patterns from analysis work cases.",
        ),
    ),
    SpecialistIntelligenceProfile(
        guardian_id="evaluation-judge-specialist",
        role="Evaluation Judge Guardian",
        capabilities=frozenset(
            {
                "evaluation",
                "llm-as-judge",
                "correctness-grading",
                "trajectory-evaluation",
                "benchmark-evaluation",
            }
        ),
        benchmark_tags=frozenset({"evaluation", "quality", "benchmark", "reliability"}),
        learning_objectives=(
            "Improve grading accuracy against ground truth with calibrated judges.",
            "Learn evaluator biases and failure modes from scored trajectories.",
        ),
    ),
)


class AdaptiveGuardianIntelligence:
    """Evidence-driven specialist learning without live model-weight mutation.

    The engine adapts routing and training priorities from verified outcomes. It never grants
    permissions and does not rewrite model weights, prompts, or benchmark truth by itself.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._profiles = {profile.guardian_id: profile for profile in SPECIALIST_INTELLIGENCE_PROFILES}
        self._states = self._load()
        for profile in SPECIALIST_INTELLIGENCE_PROFILES:
            self._states.setdefault(
                profile.guardian_id,
                GuardianAdaptiveState(guardian_id=profile.guardian_id, role=profile.role),
            )
        self._save()

    def profiles(self) -> tuple[SpecialistIntelligenceProfile, ...]:
        return SPECIALIST_INTELLIGENCE_PROFILES

    def profile(self, guardian_id: str) -> SpecialistIntelligenceProfile:
        try:
            return self._profiles[guardian_id]
        except KeyError as exc:
            raise KeyError(f"unknown adaptive specialist Guardian: {guardian_id}") from exc

    def state(self, guardian_id: str) -> GuardianAdaptiveState:
        try:
            return self._states[guardian_id]
        except KeyError as exc:
            raise KeyError(f"unknown adaptive specialist Guardian: {guardian_id}") from exc

    def record_verified_outcome(
        self,
        guardian_id: str,
        *,
        skills: frozenset[str],
        success: bool,
        score: float,
        benchmark_passed: bool | None = None,
        critical_regression: bool = False,
        verified: bool,
    ) -> GuardianAdaptiveState:
        if not verified:
            raise ValueError("adaptive learning requires a verified outcome")
        if not 0 <= score <= 10:
            raise ValueError("score must be between 0 and 10")
        if not skills:
            raise ValueError("adaptive learning requires at least one skill")

        state = self.state(guardian_id)
        for skill in skills:
            if not skill.strip():
                continue
            evidence = state.skills.setdefault(skill, SkillEvidence())
            evidence.attempts += 1
            evidence.successes += int(success)
            evidence.total_score += score
            if benchmark_passed is True:
                evidence.benchmark_passes += 1
            elif benchmark_passed is False:
                evidence.benchmark_failures += 1
            evidence.critical_regressions += int(critical_regression)
            evidence.recent_scores.append(score)
            del evidence.recent_scores[:-20]
            evidence.updated_at = time.time()

        state.verified_runs += 1
        state.learning_cycles += 1
        state.last_learning_at = time.time()
        self._save()
        return state

    def routing_bonus(self, guardian_id: str, required_capabilities: frozenset[str]) -> float:
        """Return a bounded evidence bonus for routing; unknown evidence remains neutral."""
        state = self._states.get(guardian_id)
        if state is None or not required_capabilities:
            return 0.0
        scores = [
            state.skills[skill].adaptive_score
            for skill in required_capabilities
            if skill in state.skills
        ]
        if not scores:
            return 0.0
        average = sum(scores) / len(scores)
        return max(-1.5, min(1.5, (average - 5.0) * 0.30))

    def training_priorities(self, guardian_id: str, *, limit: int = 5) -> list[TrainingPriority]:
        if limit < 1:
            return []
        profile = self.profile(guardian_id)
        state = self.state(guardian_id)
        priorities: list[TrainingPriority] = []
        for skill in profile.capabilities:
            evidence = state.skills.get(skill, SkillEvidence())
            score = evidence.adaptive_score
            confidence = evidence.confidence
            uncertainty = 1.0 - confidence
            regression_pressure = min(1.0, evidence.critical_regressions / 2.0)
            weakness = max(0.0, (7.5 - score) / 7.5)
            priority = (weakness * 0.60) + (uncertainty * 0.25) + (regression_pressure * 0.15)
            rationale_parts = []
            if evidence.attempts == 0:
                rationale_parts.append("no verified evidence yet")
            if score < 7.5:
                rationale_parts.append(f"adaptive score {score:.2f}/10")
            if evidence.trend < -0.25:
                rationale_parts.append("recent performance trend is declining")
            if evidence.critical_regressions:
                rationale_parts.append(
                    f"{evidence.critical_regressions} critical regression(s) observed"
                )
            priorities.append(
                TrainingPriority(
                    skill=skill,
                    score=score,
                    confidence=confidence,
                    priority=priority,
                    rationale="; ".join(rationale_parts) or "maintain benchmark proficiency",
                )
            )
        priorities.sort(key=lambda item: (item.priority, -item.score), reverse=True)
        return priorities[:limit]

    def intelligence_summary(self, guardian_id: str) -> dict[str, object]:
        state = self.state(guardian_id)
        profile = self.profile(guardian_id)
        skill_scores = {
            skill: round(state.skills.get(skill, SkillEvidence()).adaptive_score, 3)
            for skill in sorted(profile.capabilities)
        }
        priorities = self.training_priorities(guardian_id)
        return {
            "guardian_id": guardian_id,
            "role": profile.role,
            "verified_runs": state.verified_runs,
            "learning_cycles": state.learning_cycles,
            "skill_scores": skill_scores,
            "training_priorities": [asdict(item) for item in priorities],
        }

    def _load(self) -> dict[str, GuardianAdaptiveState]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        if not isinstance(payload, dict):
            return {}
        states: dict[str, GuardianAdaptiveState] = {}
        for guardian_id, raw_state in payload.items():
            if not isinstance(raw_state, dict):
                continue
            raw_skills = raw_state.get("skills", {})
            skills: dict[str, SkillEvidence] = {}
            if isinstance(raw_skills, dict):
                for skill, raw_evidence in raw_skills.items():
                    if not isinstance(raw_evidence, dict):
                        continue
                    try:
                        skills[skill] = SkillEvidence(**raw_evidence)
                    except TypeError:
                        continue
            try:
                states[guardian_id] = GuardianAdaptiveState(
                    guardian_id=guardian_id,
                    role=str(raw_state.get("role", guardian_id)),
                    skills=skills,
                    verified_runs=int(raw_state.get("verified_runs", 0)),
                    learning_cycles=int(raw_state.get("learning_cycles", 0)),
                    last_learning_at=float(raw_state.get("last_learning_at", 0.0)),
                )
            except (TypeError, ValueError):
                continue
        return states

    def _save(self) -> None:
        payload: dict[str, object] = {}
        for guardian_id, state in self._states.items():
            record = asdict(state)
            payload[guardian_id] = record
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
