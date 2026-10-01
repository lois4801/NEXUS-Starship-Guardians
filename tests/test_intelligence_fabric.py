from nexus_os.adversarial_eval import AdversarialCaseGenerator
from nexus_os.intelligence_fabric import IntelligenceFabric
from nexus_os.knowledge_graph import KnowledgeEdge, KnowledgeGraph, KnowledgeNode
from nexus_os.memory_quality import MemoryQualityRegistry
from nexus_os.model_registry import ModelProfile, ModelRegistry
from nexus_os.strategy_engine import StrategyMode


def test_knowledge_graph_tracks_impact_paths():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode("api", "module", "API", "lucio"))
    graph.add_node(KnowledgeNode("auth", "module", "Auth", "lucio"))
    graph.add_node(KnowledgeNode("tests", "suite", "Auth tests", "lucio"))
    graph.add_edge(KnowledgeEdge("auth", "api", "used_by"))
    graph.add_edge(KnowledgeEdge("api", "tests", "covered_by"))
    result = graph.impact("auth")
    assert result.affected == ("api", "tests")
    assert result.paths["tests"] == ("auth", "api", "tests")


def test_intelligence_fabric_selects_security_first_and_adversarial_checks():
    plan = IntelligenceFabric().plan(
        "Deploy a secure FastAPI API with PostgreSQL migration, OAuth permissions, and tests"
    )
    assert plan.strategy.mode is StrategyMode.SECURITY_FIRST
    assert "security review" in plan.strategy.required_evidence
    case_ids = {case.case_id for case in plan.adversarial_cases}
    assert "permission-escalation" in case_ids
    assert "unsafe-schema-change" in case_ids
    assert "deploy-without-proof" in case_ids
    assert 0 <= plan.uncertainty <= 1


def test_adversarial_generator_has_general_completion_guardrail():
    cases = AdversarialCaseGenerator().generate("Explain this architecture")
    assert [case.case_id for case in cases] == ["unsupported-completion"]


def test_model_registry_ranks_verified_task_performance():
    registry = ModelRegistry()
    registry.register(ModelProfile("model-a", "provider-a", frozenset({"backend"})))
    registry.register(ModelProfile("model-b", "provider-b", frozenset({"backend"})))
    registry.record_outcome("model-a", task_category="backend", success=True, score=9.2, cost=1.0, latency_seconds=8)
    registry.record_outcome("model-b", task_category="backend", success=True, score=8.0, cost=1.0, latency_seconds=8)
    assert [item.profile.model_id for item in registry.rank("backend")] == ["model-a", "model-b"]


def test_memory_quality_quarantines_repeatedly_harmful_memory():
    registry = MemoryQualityRegistry(quarantine_threshold=0.4, minimum_observations=3)
    registry.register("lesson-1", confidence=0.4)
    registry.record_reuse("lesson-1", "harmful")
    registry.record_reuse("lesson-1", "harmful")
    item = registry.record_reuse("lesson-1", "harmful")
    assert item.quarantined is True
    assert registry.eligible("lesson-1") is False
