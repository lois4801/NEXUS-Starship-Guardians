"""Small, strictly allowlisted tool registry. No arbitrary Python or shell execution."""

import ast
import operator
from datetime import UTC, datetime
from typing import Any

from .storage import Store


class ToolError(ValueError):
    pass


_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _calculate(node: ast.AST, depth: int = 0) -> float | int:
    if depth > 12:
        raise ToolError("Expression is too deep")
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        if abs(node.value) > 1_000_000_000:
            raise ToolError("Number is too large")
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        a = _calculate(node.left, depth + 1)
        b = _calculate(node.right, depth + 1)
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and b == 0:
            raise ToolError("Division by zero")
        out = _OPS[type(node.op)](a, b)
        if abs(out) > 1_000_000_000_000:
            raise ToolError("Result is too large")
        return out
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_calculate(node.operand, depth + 1))
    raise ToolError("Unsupported expression")


TOOL_DESCRIPTIONS = {
    "calculator": "Calculate basic arithmetic. Arguments: {expression: string}.",
    "utc_now": "Retrieve the server's current UTC time. Arguments: {}.",
    "project_note": "Write a project-specific note. Requires approval. Arguments: {content: string}.",
}
APPROVAL_REQUIRED = {"project_note"}


def run_tool(name: str, args: dict[str, Any], project_id: str, store: Store) -> dict[str, Any]:
    if name == "calculator":
        expression = args.get("expression")
        if not isinstance(expression, str) or not 1 <= len(expression) <= 100:
            raise ToolError("expression must be 1–100 characters")
        try:
            value = _calculate(ast.parse(expression, mode="eval").body)
            return {"result": value}
        except (SyntaxError, ValueError, ArithmeticError, OverflowError) as exc:
            raise ToolError(f"Invalid arithmetic: {exc}") from exc
    if name == "utc_now":
        return {"utc": datetime.now(UTC).isoformat()}
    if name == "project_note":
        content = args.get("content")
        if not isinstance(content, str) or not 1 <= len(content) <= 3000:
            raise ToolError("content must be 1–3000 characters")
        return {"note_id": store.add_note(project_id, content)}
    raise ToolError("Unknown tool")
