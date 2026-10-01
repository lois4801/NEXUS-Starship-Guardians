from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CapabilityRule:
    capability: str
    keywords: tuple[str, ...]
    tools: frozenset[str] = frozenset()
    weight: int = 1


@dataclass(frozen=True, slots=True)
class CapabilityMatch:
    capabilities: frozenset[str]
    tools: frozenset[str]
    matched_rules: tuple[str, ...]


DEFAULT_CAPABILITY_RULES: tuple[CapabilityRule, ...] = (
    CapabilityRule("frontend", ("react", "frontend", "ui", "component", "css", "animation"), frozenset({"browser"}), 3),
    CapabilityRule("backend", ("backend", "fastapi", "api", "server", "endpoint"), frozenset({"api"}), 3),
    CapabilityRule("database", ("database", "postgres", "sql", "schema", "migration"), frozenset({"database"}), 3),
    CapabilityRule("testing", ("test", "pytest", "playwright", "verify", "regression"), frozenset({"test"}), 2),
    CapabilityRule("security", ("security", "auth", "oauth", "permission", "secret", "vulnerability"), frozenset({"security"}), 3),
    CapabilityRule("devops", ("docker", "railway", "deploy", "ci", "cd", "hosting"), frozenset({"terminal"}), 2),
    CapabilityRule("observability", ("trace", "telemetry", "opentelemetry", "metric", "logging"), frozenset({"observability"}), 2),
    CapabilityRule("ai-engineering", ("llm", "model", "prompt", "embedding", "ai", "inference"), frozenset({"model"}), 2),
    CapabilityRule("integration", ("mcp", "supabase", "github", "integration", "webhook"), frozenset({"integration"}), 2),
    CapabilityRule("architecture", ("architecture", "design system", "scaffold", "refactor", "platform"), frozenset(), 2),
)


class CapabilityMap:
    def __init__(self, rules: tuple[CapabilityRule, ...] = DEFAULT_CAPABILITY_RULES):
        self.rules = rules

    def resolve(self, mission: str) -> CapabilityMatch:
        normalized = mission.casefold()
        capabilities: set[str] = set()
        tools: set[str] = set()
        matched: list[str] = []
        for rule in self.rules:
            if any(keyword.casefold() in normalized for keyword in rule.keywords):
                capabilities.add(rule.capability)
                tools.update(rule.tools)
                matched.append(rule.capability)
        if not capabilities:
            capabilities.add("general-engineering")
        return CapabilityMatch(
            capabilities=frozenset(capabilities),
            tools=frozenset(tools),
            matched_rules=tuple(dict.fromkeys(matched)),
        )
