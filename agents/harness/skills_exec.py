from __future__ import annotations

import importlib
from typing import Any, Callable


def resolve_callable(dotted_path: str) -> Callable[..., Any]:
    if "." not in dotted_path:
        raise ValueError(f"Invalid callable path: {dotted_path}")
    mod_name, _, attr = dotted_path.rpartition(".")
    module = importlib.import_module(mod_name)
    fn = getattr(module, attr)
    if not callable(fn):
        raise TypeError(f"Not callable: {dotted_path}")
    return fn


def run_skill(fn: Callable[..., Any], *, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> Any:
    return fn(goal=goal, prior=prior, context=context)
