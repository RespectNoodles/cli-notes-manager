from __future__ import annotations

import ast
import operator as op

_ALLOWED_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
}

_ALLOWED_UNARY = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}


class CalcError(ValueError):
    pass


def safe_eval(expr: str) -> float:
    """Safely evaluate a basic arithmetic expression without eval()."""
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise CalcError("Invalid expression") from e
    return float(_eval(node.body))


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left = _eval(node.left)
        right = _eval(node.right)
        return float(_ALLOWED_BINOPS[type(node.op)](left, right))

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return float(_ALLOWED_UNARY[type(node.op)](_eval(node.operand)))

    raise CalcError("Unsupported expression")
