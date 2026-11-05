"""treexpr.py - safe expression evaluation for feature trees (stl-re-build, harness v1).

A feature tree never holds Python code. Numeric fields are either JSON numbers or expression
strings such as "stem_R - 2*BURY" or "port_elev_deg[i]". Expressions are parsed with `ast` and
only a whitelist of nodes and functions is allowed, so a tree cannot run arbitrary code.

Names resolve, in order, against: loop variables of a `repeat`, node `let` bindings, tree
`let` bindings, tree `constants` (documented clearances), and params from params.json. Every
param read is recorded so the builder can report unused params (plan/measure mismatch, as v0's
Params class did).

Numeric literals other than a small allowed set are recorded as `literals`. The builder reports
them, because v0's rule still holds: no numeric literal in geometry except documented
clearances (which belong in `constants`).
"""
from __future__ import annotations

import ast
import math
from typing import Any, Callable

ALLOWED_LITERALS = {0, 1, 2, 3, 4, -1, 0.5, 90, 180, 270, 360}


def _sign(x: float) -> float:
    return 1.0 if x > 0 else (-1.0 if x < 0 else 0.0)


FUNCS: dict[str, Callable[..., Any]] = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "asin": math.asin, "acos": math.acos,
    "atan": math.atan, "atan2": math.atan2, "radians": math.radians, "degrees": math.degrees,
    "sqrt": math.sqrt, "hypot": math.hypot, "abs": abs, "min": min, "max": max, "len": len,
    "range": lambda *a: list(range(*a)), "sign": _sign, "round": round, "sum": sum,
    "float": float, "int": int, "sind": lambda d: math.sin(math.radians(d)),
    "cosd": lambda d: math.cos(math.radians(d)), "tand": lambda d: math.tan(math.radians(d)),
}
CONSTS = {"pi": math.pi, "True": True, "False": False}

_BIN = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b, ast.Pow: lambda a, b: a ** b, ast.Mod: lambda a, b: a % b,
        ast.FloorDiv: lambda a, b: a // b}
_CMP = {ast.Lt: lambda a, b: a < b, ast.LtE: lambda a, b: a <= b, ast.Gt: lambda a, b: a > b,
        ast.GtE: lambda a, b: a >= b, ast.Eq: lambda a, b: a == b, ast.NotEq: lambda a, b: a != b}


class ExprError(ValueError):
    pass


class Scope:
    """Name lookup chain. `params` is the params.json dict {name: {value, source, ...}}."""

    def __init__(self, params: dict[str, dict[str, Any]], constants: dict[str, Any] | None = None) -> None:
        self.params = params
        self.constants = dict(constants or {})
        self.layers: list[dict[str, Any]] = []
        self.used: set[str] = set()
        self.literals: list[tuple[str, float]] = []
        self.context = ""

    def push(self, layer: dict[str, Any]) -> None:
        self.layers.append(layer)

    def pop(self) -> None:
        self.layers.pop()

    def lookup(self, name: str) -> Any:
        for layer in reversed(self.layers):
            if name in layer:
                return layer[name]
        if name in self.constants:
            return self.constants[name]
        if name in self.params:
            self.used.add(name)
            return self.params[name]["value"]
        if name in CONSTS:
            return CONSTS[name]
        raise ExprError(f"unknown name {name!r}")

    def note_literal(self, v: float) -> None:
        if isinstance(v, bool) or v in ALLOWED_LITERALS:
            return
        self.literals.append((self.context, v))

    # ---------------------------------------------------------------- evaluation
    def eval(self, x: Any) -> Any:
        """Evaluate a JSON value: numbers pass through, strings are expressions, lists map."""
        if isinstance(x, bool) or x is None:
            return x
        if isinstance(x, (int, float)):
            self.note_literal(x)
            return x
        if isinstance(x, str):
            return self.eval_str(x)
        if isinstance(x, list):
            return [self.eval(v) for v in x]
        if isinstance(x, dict):
            return {k: self.eval(v) for k, v in x.items()}
        raise ExprError(f"cannot evaluate {type(x).__name__}")

    def num(self, x: Any) -> float:
        v = self.eval(x)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ExprError(f"{x!r} is not a number (got {v!r})")
        return float(v)

    def opt(self, spec: dict[str, Any], key: str, default: float) -> float:
        """spec[key] as a number, or the code default (a code default is not a tree literal)."""
        return self.num(spec[key]) if key in spec else float(default)

    def vec(self, x: Any, n: int | None = None) -> list[float]:
        v = self.eval(x)
        if not isinstance(v, (list, tuple)) or (n is not None and len(v) != n):
            raise ExprError(f"{x!r} is not a {n or ''}-vector (got {v!r})")
        return [float(c) for c in v]

    def eval_str(self, s: str) -> Any:
        try:
            tree = ast.parse(s, mode="eval")
        except SyntaxError as ex:
            raise ExprError(f"syntax error in {s!r}: {ex.msg}") from None
        try:
            return self._ev(tree.body)
        except ExprError as ex:
            raise ExprError(f"{ex} (in {s!r})") from None
        except (ZeroDivisionError, ValueError, TypeError, IndexError) as ex:
            raise ExprError(f"{type(ex).__name__}: {ex} (in {s!r})") from None

    def _ev(self, n: ast.AST) -> Any:
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
                self.note_literal(n.value)
                return n.value
            if isinstance(n.value, (str, bool)):
                return n.value
            raise ExprError(f"constant {n.value!r} not allowed")
        if isinstance(n, ast.Name):
            return self.lookup(n.id)
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
            return _BIN[type(n.op)](self._ev(n.left), self._ev(n.right))
        if isinstance(n, ast.UnaryOp):
            v = self._ev(n.operand)
            if isinstance(n.op, ast.USub):
                return -v
            if isinstance(n.op, ast.UAdd):
                return +v
            if isinstance(n.op, ast.Not):
                return not v
        if isinstance(n, ast.Compare):
            left = self._ev(n.left)
            for op, comp in zip(n.ops, n.comparators):
                right = self._ev(comp)
                if type(op) not in _CMP or not _CMP[type(op)](left, right):
                    return False
                left = right
            return True
        if isinstance(n, ast.BoolOp):
            vals = [self._ev(v) for v in n.values]
            return all(vals) if isinstance(n.op, ast.And) else any(vals)
        if isinstance(n, ast.IfExp):
            return self._ev(n.body) if self._ev(n.test) else self._ev(n.orelse)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FUNCS and not n.keywords:
            return FUNCS[n.func.id](*[self._ev(a) for a in n.args])
        if isinstance(n, ast.Subscript):
            base = self._ev(n.value)
            idx = self._ev(n.slice)
            return base[int(idx)]
        if isinstance(n, (ast.List, ast.Tuple)):
            return [self._ev(e) for e in n.elts]
        raise ExprError(f"expression element {type(n).__name__} not allowed")


def bind_let(scope: Scope, let: dict[str, Any] | None) -> dict[str, Any]:
    """Evaluate `let` bindings in order (later ones may use earlier ones) into a new layer."""
    layer: dict[str, Any] = {}
    scope.push(layer)
    try:
        for k, v in (let or {}).items():
            layer[k] = scope.eval(v)
    finally:
        scope.pop()
    return layer


def repeat_instances(scope: Scope, repeat: dict[str, Any] | None) -> list[dict[str, Any]]:
    """`repeat: {var: list-expr, ...}` -> one binding dict per instance (lists are zipped).
    No repeat -> one empty instance. An empty list raises: a pattern never places 0 instances
    unnoticed (v0 Params.group rule)."""
    if not repeat:
        return [{}]
    cols = {k: scope.eval(v) for k, v in repeat.items()}
    lens = {k: len(v) for k, v in cols.items() if isinstance(v, list)}
    if len(lens) != len(cols):
        raise ExprError(f"repeat values must be lists: {cols}")
    if len(set(lens.values())) != 1:
        raise ExprError(f"repeat lists differ in length: {lens}")
    n = next(iter(lens.values()))
    if n == 0:
        raise ExprError("repeat over an empty list")
    return [{k: cols[k][i] for k in cols} | {"_n": i} for i in range(n)]
