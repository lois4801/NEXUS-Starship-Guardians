from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class KnowledgeNode:
    node_id: str
    kind: str
    label: str
    project_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class KnowledgeEdge:
    source: str
    target: str
    relation: str


@dataclass(frozen=True, slots=True)
class ImpactResult:
    origin: str
    affected: tuple[str, ...]
    paths: dict[str, tuple[str, ...]]


class KnowledgeGraph:
    """Small in-memory directed graph for inspectable project/system relationships."""

    def __init__(self) -> None:
        self._nodes: dict[str, KnowledgeNode] = {}
        self._outgoing: dict[str, list[KnowledgeEdge]] = {}
        self._incoming: dict[str, list[KnowledgeEdge]] = {}

    def add_node(self, node: KnowledgeNode) -> None:
        if not node.node_id.strip():
            raise ValueError("node_id cannot be empty")
        if node.node_id in self._nodes:
            raise ValueError(f"duplicate knowledge node: {node.node_id}")
        self._nodes[node.node_id] = node
        self._outgoing[node.node_id] = []
        self._incoming[node.node_id] = []

    def add_edge(self, edge: KnowledgeEdge) -> None:
        if edge.source not in self._nodes or edge.target not in self._nodes:
            raise KeyError("knowledge edge endpoints must already exist")
        if edge.source == edge.target:
            raise ValueError("self edges are not allowed")
        self._outgoing[edge.source].append(edge)
        self._incoming[edge.target].append(edge)

    def get(self, node_id: str) -> KnowledgeNode:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"unknown knowledge node: {node_id}") from exc

    def neighbors(self, node_id: str, *, relation: str | None = None) -> tuple[KnowledgeNode, ...]:
        self.get(node_id)
        edges = self._outgoing[node_id]
        if relation is not None:
            edges = [edge for edge in edges if edge.relation == relation]
        return tuple(self._nodes[edge.target] for edge in edges)

    def impact(self, node_id: str, *, max_depth: int = 6) -> ImpactResult:
        if max_depth < 1:
            raise ValueError("max_depth must be at least 1")
        self.get(node_id)
        queue = deque([(node_id, (node_id,), 0)])
        seen = {node_id}
        paths: dict[str, tuple[str, ...]] = {}
        while queue:
            current, path, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in self._outgoing[current]:
                if edge.target in seen:
                    continue
                seen.add(edge.target)
                next_path = (*path, edge.target)
                paths[edge.target] = next_path
                queue.append((edge.target, next_path, depth + 1))
        affected = tuple(paths)
        return ImpactResult(origin=node_id, affected=affected, paths=paths)

    def project_nodes(self, project_id: str) -> tuple[KnowledgeNode, ...]:
        return tuple(node for node in self._nodes.values() if node.project_id == project_id)
