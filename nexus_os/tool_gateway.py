from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GatewayToolSpec:
    name: str
    capability: str
    approval_required: bool = False
    external: bool = True


@dataclass(frozen=True, slots=True)
class GatewayAuthorization:
    tool: str
    enabled_for_project: bool
    permitted_by_guardian: bool
    allowed: bool
    reason: str


DEFAULT_GATEWAY_TOOLS: tuple[GatewayToolSpec, ...] = (
    GatewayToolSpec("browser", "frontend"),
    GatewayToolSpec("api", "backend"),
    GatewayToolSpec("database", "database", approval_required=True),
    GatewayToolSpec("test", "testing"),
    GatewayToolSpec("security", "security"),
    GatewayToolSpec("terminal", "devops", approval_required=True),
    GatewayToolSpec("observability", "observability"),
    GatewayToolSpec("model", "ai-engineering"),
    GatewayToolSpec("integration", "integration", approval_required=True),
)


class ControlledToolGateway:
    """Permission policy for high-level external tools.

    This layer does not implement external connectivity. It only answers whether a project and a
    selected Guardian are jointly allowed to use a named gateway tool. Real adapters (MCP, Railway,
    Supabase, browser, etc.) must remain separate, authenticated integrations.
    """

    def __init__(self, specs: tuple[GatewayToolSpec, ...] = DEFAULT_GATEWAY_TOOLS):
        self._specs = {spec.name: spec for spec in specs}

    def spec(self, name: str) -> GatewayToolSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"unknown gateway tool: {name}") from exc

    def authorize(
        self,
        name: str,
        *,
        project_tools: frozenset[str],
        guardian_tools: frozenset[str],
    ) -> GatewayAuthorization:
        self.spec(name)
        project_enabled = name in project_tools
        guardian_permitted = name in guardian_tools
        allowed = project_enabled and guardian_permitted
        if not project_enabled:
            reason = "tool is not enabled for this project"
        elif not guardian_permitted:
            reason = "selected Guardian is not permitted to use this tool"
        else:
            reason = "project and Guardian permissions allow this tool"
        return GatewayAuthorization(
            tool=name,
            enabled_for_project=project_enabled,
            permitted_by_guardian=guardian_permitted,
            allowed=allowed,
            reason=reason,
        )

    def blocked_tools(
        self,
        required_tools: frozenset[str],
        *,
        project_tools: frozenset[str],
    ) -> frozenset[str]:
        unknown = {tool for tool in required_tools if tool not in self._specs}
        disabled = {tool for tool in required_tools if tool not in project_tools}
        return frozenset(unknown | disabled)
