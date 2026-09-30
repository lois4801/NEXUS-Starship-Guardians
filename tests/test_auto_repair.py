import asyncio
from pathlib import Path

from nexus_os.auto_repair import VerifiedAutoRepairLoop
from nexus_os.learning_memory import GuardianLearningEngine, JsonlLearningStore


def test_auto_repair_learns_from_verified_run(tmp_path: Path):
    async def scenario():
        store = JsonlLearningStore(tmp_path / "learning.jsonl")
        learning = GuardianLearningEngine(store)
        loop = VerifiedAutoRepairLoop(max_rounds=3, learning=learning)

        async def build():
            return "version-1"

        async def verify(candidate: str):
            if candidate == "version-2":
                return True, "tests passed"
            return False, "expected version-2"

        async def repair(candidate: str, verification: str, round_number: int):
            assert candidate == "version-1"
            assert "version-2" in verification
            assert round_number == 1
            return "version-2"

        async def reflect(task: str, candidate: str, verification: str):
            return "When this verifier fails, produce version-2 and rerun the tests."

        report = await loop.run("upgrade version", build, verify, repair, reflect=reflect)
        assert report.passed
        assert len(report.rounds) == 2
        assert report.evidence is not None and report.evidence.verify()
        assert "version-2" in learning.context_for("verifier version")

    asyncio.run(scenario())


def test_auto_repair_stops_at_bound():
    async def scenario():
        loop = VerifiedAutoRepairLoop(max_rounds=2)

        async def build():
            return "broken"

        async def verify(candidate: str):
            return False, f"still failing: {candidate}"

        async def repair(candidate: str, verification: str, round_number: int):
            return candidate + "-retry"

        report = await loop.run("bounded failure", build, verify, repair)
        assert not report.passed
        assert len(report.rounds) == 2

    asyncio.run(scenario())
