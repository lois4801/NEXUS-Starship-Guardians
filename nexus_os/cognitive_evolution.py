from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .adaptive_intelligence import AdaptiveGuardianIntelligence


@dataclass(frozen=True, slots=True)
class CognitiveLesson:
    lesson_id: str
    source_guardian: str
    skills: tuple[str, ...]
    success: bool
    score: float
    evidence_strength: float
    summary: str
    strategy: str
    failure_signature: str
    created_at: float


@dataclass(slots=True)
class ConfidenceCalibration:
    predictions: int = 0
    brier_total: float = 0.0

    @property
    def brier_score(self) -> float:
        return self.brier_total / self.predictions if self.predictions else 0.25

    @property
    def reliability(self) -> float:
        return max(0.0, min(1.0, 1.0 - self.brier_score))


@dataclass(slots=True)
class GuardianCognitiveState:
    guardian_id: str
    verified_episodes: int = 0
    authored_lessons: int = 0
    counterfactual_cycles: int = 0
    calibration: ConfidenceCalibration = field(default_factory=ConfidenceCalibration)
    last_learning_at: float = 0.0


@dataclass(slots=True)
class FailureCluster:
    signature: str
    count: int = 0
    guardians: set[str] = field(default_factory=set)
    skills: set[str] = field(default_factory=set)
    last_seen: float = 0.0


@dataclass(frozen=True, slots=True)
class CounterfactualReplayPlan:
    guardian_id: str
    focus_skills: tuple[str, ...]
    failure_signature: str
    original_strategy: str
    alternative_strategies: tuple[str, ...]
    objective: str


@dataclass(frozen=True, slots=True)
class CurriculumItem:
    guardian_id: str
    skill: str
    priority: float
    rationale: str
    exercises: tuple[str, ...]
    transferable_lessons: tuple[str, ...]


class CognitiveEvolutionEngine:
    """Persistent meta-learning for specialist Guardians.

    Cognitive Evolution learns from verified episodes, creates reusable lessons, clusters recurring
    failures, calibrates confidence, proposes counterfactual strategies, and builds self-curricula.
    Shared lessons can inform another Guardian, but they never transfer performance scores or grant
    tool permissions. Live model-weight mutation is deliberately outside this engine.
    """

    def __init__(self, path: Path, adaptive: AdaptiveGuardianIntelligence):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.adaptive = adaptive
        self._states: dict[str, GuardianCognitiveState] = {}
        self._lessons: list[CognitiveLesson] = []
        self._failures: dict[str, FailureCluster] = {}
        self._load()
        for profile in adaptive.profiles():
            self._states.setdefault(
                profile.guardian_id,
                GuardianCognitiveState(guardian_id=profile.guardian_id),
            )
        self._save()

    def state(self, guardian_id: str) -> GuardianCognitiveState:
        self.adaptive.profile(guardian_id)
        return self._states[guardian_id]

    def lessons(self) -> tuple[CognitiveLesson, ...]:
        return tuple(self._lessons)

    def failure_clusters(self) -> tuple[FailureCluster, ...]:
        return tuple(sorted(self._failures.values(), key=lambda item: item.count, reverse=True))

    def record_verified_episode(
        self,
        guardian_id: str,
        *,
        skills: frozenset[str],
        success: bool,
        score: float,
        summary: str,
        strategy: str = "",
        failure_signature: str = "",
        predicted_confidence: float | None = None,
        verified: bool,
    ) -> CognitiveLesson:
        if not verified:
            raise ValueError("cognitive evolution requires verified evidence")
        if not skills:
            raise ValueError("cognitive evolution requires at least one skill")
        if not 0 <= score <= 10:
            raise ValueError("score must be between 0 and 10")
        if predicted_confidence is not None and not 0 <= predicted_confidence <= 1:
            raise ValueError("predicted_confidence must be between 0 and 1")

        self.adaptive.profile(guardian_id)
        state = self._states[guardian_id]
        now = time.time()
        normalized_summary = " ".join(summary.split()).strip() or (
            "Verified success." if success else "Verified failure."
        )
        ordered_skills = tuple(sorted(skill for skill in skills if skill.strip()))
        lesson_key = "|".join(
            [
                guardian_id,
                ",".join(ordered_skills),
                str(success),
                strategy.strip(),
                failure_signature.strip(),
                normalized_summary,
            ]
        )
        lesson_id = hashlib.sha256(lesson_key.encode("utf-8")).hexdigest()[:20]
        evidence_strength = max(0.05, min(1.0, score / 10.0 if success else (10.0 - score) / 10.0))
        lesson = CognitiveLesson(
            lesson_id=lesson_id,
            source_guardian=guardian_id,
            skills=ordered_skills,
            success=success,
            score=score,
            evidence_strength=evidence_strength,
            summary=normalized_summary,
            strategy=strategy.strip(),
            failure_signature=failure_signature.strip(),
            created_at=now,
        )
        if not any(existing.lesson_id == lesson.lesson_id for existing in self._lessons):
            self._lessons.append(lesson)
            state.authored_lessons += 1

        state.verified_episodes += 1
        state.last_learning_at = now
        if predicted_confidence is not None:
            target = 1.0 if success else 0.0
            state.calibration.predictions += 1
            state.calibration.brier_total += (predicted_confidence - target) ** 2

        if not success:
            signature = failure_signature.strip() or "unclassified-failure"
            cluster = self._failures.setdefault(signature, FailureCluster(signature=signature))
            cluster.count += 1
            cluster.guardians.add(guardian_id)
            cluster.skills.update(ordered_skills)
            cluster.last_seen = now

        self._save()
        return lesson

    def shared_lessons(
        self,
        target_guardian: str,
        *,
        skills: frozenset[str],
        limit: int = 5,
    ) -> list[CognitiveLesson]:
        if limit < 1:
            return []
        profile = self.adaptive.profile(target_guardian)
        relevant_skills = skills or profile.capabilities
        ranked: list[tuple[float, CognitiveLesson]] = []
        for lesson in self._lessons:
            overlap = len(set(lesson.skills) & set(relevant_skills))
            if overlap == 0:
                continue
            source_bonus = 0.05 if lesson.source_guardian == target_guardian else 0.0
            rank = (overlap * 2.0) + lesson.evidence_strength + source_bonus
            ranked.append((rank, lesson))
        ranked.sort(key=lambda item: (item[0], item[1].created_at), reverse=True)
        return [lesson for _, lesson in ranked[:limit]]

    def counterfactual_plan(
        self,
        guardian_id: str,
        *,
        skills: frozenset[str],
        failure_signature: str,
        original_strategy: str = "",
    ) -> CounterfactualReplayPlan:
        self.adaptive.profile(guardian_id)
        normalized = f"{failure_signature} {' '.join(skills)}".casefold()
        strategies: list[str] = []
        if any(token in normalized for token in ("debug", "error", "regression", "test", "repair")):
            strategies.extend(
                ["minimal-reproduction", "hypothesis-first-debugging", "binary-isolation"]
            )
        if any(token in normalized for token in ("security", "auth", "permission", "credential")):
            strategies.extend(["threat-model-first", "least-privilege-review", "adversarial-test"])
        if any(token in normalized for token in ("database", "schema", "migration", "sql")):
            strategies.extend(["schema-diff-first", "transactional-rehearsal", "rollback-first"])
        if any(token in normalized for token in ("api", "contract", "http", "integration")):
            strategies.extend(["contract-first", "mock-provider-replay", "failure-injection"])
        if any(token in normalized for token in ("cloud", "deploy", "container", "infra")):
            strategies.extend(["staged-rollout", "health-gate-first", "rollback-simulation"])
        if any(token in normalized for token in ("architecture", "platform", "design")):
            strategies.extend(["constraint-first-design", "tradeoff-matrix", "failure-mode-review"])
        if not strategies:
            strategies.extend(["baseline-replay", "alternate-decomposition", "independent-review"])
        unique = tuple(dict.fromkeys(strategies))[:5]
        state = self.state(guardian_id)
        state.counterfactual_cycles += 1
        self._save()
        return CounterfactualReplayPlan(
            guardian_id=guardian_id,
            focus_skills=tuple(sorted(skills)),
            failure_signature=failure_signature,
            original_strategy=original_strategy,
            alternative_strategies=unique,
            objective="Replay the verified failure under materially different strategies and compare evidence.",
        )

    def curriculum(self, guardian_id: str, *, limit: int = 5) -> list[CurriculumItem]:
        if limit < 1:
            return []
        priorities = self.adaptive.training_priorities(guardian_id, limit=limit)
        curriculum: list[CurriculumItem] = []
        for priority in priorities:
            shared = self.shared_lessons(
                guardian_id,
                skills=frozenset({priority.skill}),
                limit=3,
            )
            failure_count = sum(
                cluster.count
                for cluster in self._failures.values()
                if priority.skill in cluster.skills
            )
            rationale = priority.rationale
            if shared:
                rationale += f"; {len(shared)} verified transferable lesson(s) available"
            if failure_count:
                rationale += f"; {failure_count} recurring failure observation(s)"
            curriculum.append(
                CurriculumItem(
                    guardian_id=guardian_id,
                    skill=priority.skill,
                    priority=min(1.0, priority.priority + min(0.2, failure_count * 0.03)),
                    rationale=rationale,
                    exercises=(
                        f"Replay a verified {priority.skill} case and compare at least two strategies.",
                        f"Perform an adversarial review focused on {priority.skill} failure modes.",
                        f"Produce a teach-back lesson for {priority.skill} supported by verification evidence.",
                    ),
                    transferable_lessons=tuple(item.lesson_id for item in shared),
                )
            )
        curriculum.sort(key=lambda item: item.priority, reverse=True)
        return curriculum[:limit]

    def routing_bonus(self, guardian_id: str, required_capabilities: frozenset[str]) -> float:
        """Return a tiny bounded meta-learning bonus; permissions remain completely separate."""
        state = self._states.get(guardian_id)
        if state is None or not required_capabilities or state.verified_episodes == 0:
            return 0.0
        authored_overlap = sum(
            1
            for lesson in self._lessons
            if lesson.source_guardian == guardian_id
            and set(lesson.skills) & set(required_capabilities)
        )
        calibration_term = (state.calibration.reliability - 0.75) * 0.4
        evidence_term = min(0.2, authored_overlap * 0.02)
        return max(-0.25, min(0.35, calibration_term + evidence_term))

    def summary(self, guardian_id: str) -> dict[str, object]:
        state = self.state(guardian_id)
        curriculum = self.curriculum(guardian_id)
        authored = [item for item in self._lessons if item.source_guardian == guardian_id]
        return {
            "guardian_id": guardian_id,
            "verified_episodes": state.verified_episodes,
            "authored_lessons": state.authored_lessons,
            "counterfactual_cycles": state.counterfactual_cycles,
            "confidence_reliability": round(state.calibration.reliability, 4),
            "recent_lessons": [asdict(item) for item in authored[-5:]],
            "curriculum": [asdict(item) for item in curriculum],
        }

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return
        if not isinstance(payload, dict):
            return

        raw_states = payload.get("guardians", {})
        if isinstance(raw_states, dict):
            for guardian_id, raw in raw_states.items():
                if not isinstance(raw, dict):
                    continue
                calibration_raw = raw.get("calibration", {})
                calibration = ConfidenceCalibration()
                if isinstance(calibration_raw, dict):
                    try:
                        calibration = ConfidenceCalibration(
                            predictions=int(calibration_raw.get("predictions", 0)),
                            brier_total=float(calibration_raw.get("brier_total", 0.0)),
                        )
                    except (TypeError, ValueError):
                        calibration = ConfidenceCalibration()
                try:
                    self._states[guardian_id] = GuardianCognitiveState(
                        guardian_id=guardian_id,
                        verified_episodes=int(raw.get("verified_episodes", 0)),
                        authored_lessons=int(raw.get("authored_lessons", 0)),
                        counterfactual_cycles=int(raw.get("counterfactual_cycles", 0)),
                        calibration=calibration,
                        last_learning_at=float(raw.get("last_learning_at", 0.0)),
                    )
                except (TypeError, ValueError):
                    continue

        raw_lessons = payload.get("lessons", [])
        if isinstance(raw_lessons, list):
            for raw in raw_lessons:
                if not isinstance(raw, dict):
                    continue
                try:
                    raw["skills"] = tuple(raw.get("skills", ()))
                    self._lessons.append(CognitiveLesson(**raw))
                except (TypeError, ValueError):
                    continue

        raw_failures = payload.get("failures", {})
        if isinstance(raw_failures, dict):
            for signature, raw in raw_failures.items():
                if not isinstance(raw, dict):
                    continue
                try:
                    self._failures[signature] = FailureCluster(
                        signature=signature,
                        count=int(raw.get("count", 0)),
                        guardians=set(raw.get("guardians", [])),
                        skills=set(raw.get("skills", [])),
                        last_seen=float(raw.get("last_seen", 0.0)),
                    )
                except (TypeError, ValueError):
                    continue

    def _save(self) -> None:
        payload = {
            "guardians": {
                guardian_id: asdict(state) for guardian_id, state in self._states.items()
            },
            "lessons": [asdict(item) for item in self._lessons[-2000:]],
            "failures": {
                signature: {
                    "signature": cluster.signature,
                    "count": cluster.count,
                    "guardians": sorted(cluster.guardians),
                    "skills": sorted(cluster.skills),
                    "last_seen": cluster.last_seen,
                }
                for signature, cluster in self._failures.items()
            },
        }
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
