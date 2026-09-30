from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

_TOKEN = re.compile(r"[A-Za-z0-9_]{3,}")


@dataclass(slots=True)
class LearningEpisode:
    run_id: str
    task: str
    deliverable: str
    score: float
    critique: str
    rounds: int
    evidence_refs: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)
    type: str = "episode"


@dataclass(slots=True)
class LearningLesson:
    lesson_id: str
    text: str
    tags: tuple[str, ...] = ()
    source_run_id: str | None = None
    ts: float = field(default_factory=time.time)
    type: str = "lesson"


class JsonlLearningStore:
    """Append-only episodic memory and reusable lessons for Nexus Starship Guardians."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _append(self, record: dict) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def add_episode(
        self,
        *,
        task: str,
        deliverable: str,
        score: float,
        critique: str,
        rounds: int,
        evidence_refs: tuple[str, ...] = (),
        metadata: dict[str, str] | None = None,
        run_id: str | None = None,
    ) -> LearningEpisode:
        episode = LearningEpisode(
            run_id=run_id or uuid.uuid4().hex,
            task=task,
            deliverable=deliverable,
            score=float(score),
            critique=critique,
            rounds=rounds,
            evidence_refs=evidence_refs,
            metadata=metadata or {},
        )
        self._append(asdict(episode))
        return episode

    def add_lesson(
        self,
        text: str,
        *,
        tags: tuple[str, ...] = (),
        source_run_id: str | None = None,
    ) -> LearningLesson:
        if not text.strip():
            raise ValueError("lesson text cannot be empty")
        lesson = LearningLesson(
            lesson_id=uuid.uuid4().hex,
            text=text.strip(),
            tags=tags,
            source_run_id=source_run_id,
        )
        self._append(asdict(lesson))
        return lesson

    def records(self) -> list[dict]:
        if not self.path.exists():
            return []
        items: list[dict] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return items

    def relevant_lessons(self, query: str, *, limit: int = 8) -> list[LearningLesson]:
        if limit < 1:
            return []
        query_terms = {item.lower() for item in _TOKEN.findall(query)}
        ranked: list[tuple[int, float, LearningLesson]] = []
        for record in self.records():
            if record.get("type") != "lesson":
                continue
            lesson = LearningLesson(
                lesson_id=str(record.get("lesson_id", "")),
                text=str(record.get("text", "")),
                tags=tuple(record.get("tags", ())),
                source_run_id=record.get("source_run_id"),
                ts=float(record.get("ts", 0.0)),
            )
            lesson_terms = {item.lower() for item in _TOKEN.findall(" ".join((*lesson.tags, lesson.text)))}
            overlap = len(query_terms & lesson_terms)
            ranked.append((overlap, lesson.ts, lesson))
        ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [item[2] for item in ranked[:limit]]

    def export_sft_pairs(self, target: Path, *, min_score: float = 8.0) -> int:
        count = 0
        with target.open("w", encoding="utf-8") as handle:
            for record in self.records():
                if record.get("type") != "episode" or float(record.get("score", 0)) < min_score:
                    continue
                payload = {
                    "messages": [
                        {"role": "user", "content": str(record.get("task", ""))},
                        {"role": "assistant", "content": str(record.get("deliverable", ""))},
                    ],
                    "source_run_id": record.get("run_id"),
                }
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
                count += 1
        return count


class GuardianLearningEngine:
    """Cross-run learning via memory, critique distillation, and evaluation evidence.

    This intentionally does not modify model weights in production. Optional weight updates
    belong in a separate, curated offline fine-tuning pipeline.
    """

    def __init__(self, store: JsonlLearningStore):
        self.store = store

    def context_for(self, task: str, *, limit: int = 8) -> str:
        lessons = self.store.relevant_lessons(task, limit=limit)
        if not lessons:
            return "(no prior Guardian lessons)"
        return "\n".join(f"- {lesson.text}" for lesson in lessons)

    def learn_from_run(
        self,
        *,
        task: str,
        deliverable: str,
        score: float,
        critique: str,
        rounds: int,
        distilled_lesson: str | None = None,
        evidence_refs: tuple[str, ...] = (),
        metadata: dict[str, str] | None = None,
    ) -> LearningEpisode:
        episode = self.store.add_episode(
            task=task,
            deliverable=deliverable,
            score=score,
            critique=critique,
            rounds=rounds,
            evidence_refs=evidence_refs,
            metadata=metadata,
        )
        lesson = (distilled_lesson or critique).strip()
        if lesson:
            self.store.add_lesson(lesson[:2000], source_run_id=episode.run_id)
        return episode
