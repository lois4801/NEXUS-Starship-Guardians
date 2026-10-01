from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntegrationContract:
    name: str
    description: str
    required_capabilities: frozenset[str]
    required_tools: frozenset[str]


@dataclass(frozen=True, slots=True)
class IntegrationReadiness:
    integration: str
    description: str
    connected: bool
    required_capabilities: frozenset[str]
    required_tools: frozenset[str]
    missing_capabilities: frozenset[str]
    missing_tools: frozenset[str]
    ready: bool


DEFAULT_INTEGRATION_CONTRACTS: dict[str, IntegrationContract] = {
    "lucio": IntegrationContract(
        "lucio",
        "Lucio AI Platform server-side Guardian integration contract.",
        frozenset({"integration", "backend", "security"}),
        frozenset({"integration", "api"}),
    ),
    "ember": IntegrationContract(
        "ember",
        "Ember server-side Guardian integration contract.",
        frozenset({"integration", "backend", "security"}),
        frozenset({"integration", "api"}),
    ),
    "nexus-code": IntegrationContract(
        "nexus-code",
        "Nexus Code repository and coding-workflow integration contract.",
        frozenset({"integration", "devops", "testing"}),
        frozenset({"integration", "terminal", "test"}),
    ),
    "railway": IntegrationContract(
        "railway",
        "Railway deployment integration readiness contract; no credentials are implied.",
        frozenset({"integration", "devops"}),
        frozenset({"integration", "terminal"}),
    ),
    "supabase": IntegrationContract(
        "supabase",
        "Supabase database/auth integration readiness contract; no project connection is implied.",
        frozenset({"integration", "database", "security"}),
        frozenset({"integration", "database"}),
    ),
}


class IntegrationContractRegistry:
    def __init__(self, contracts: dict[str, IntegrationContract] | None = None):
        self.contracts = contracts or DEFAULT_INTEGRATION_CONTRACTS

    def get(self, name: str) -> IntegrationContract:
        try:
            return self.contracts[name]
        except KeyError as exc:
            raise KeyError(f"unknown integration contract: {name}") from exc

    def assess(
        self,
        name: str,
        *,
        available_capabilities: frozenset[str],
        enabled_tools: frozenset[str],
        connected: bool = False,
    ) -> IntegrationReadiness:
        contract = self.get(name)
        missing_capabilities = contract.required_capabilities - available_capabilities
        missing_tools = contract.required_tools - enabled_tools
        return IntegrationReadiness(
            integration=contract.name,
            description=contract.description,
            connected=connected,
            required_capabilities=contract.required_capabilities,
            required_tools=contract.required_tools,
            missing_capabilities=frozenset(missing_capabilities),
            missing_tools=frozenset(missing_tools),
            ready=not missing_capabilities and not missing_tools,
        )
