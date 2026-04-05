from __future__ import annotations

from pathlib import Path

import yaml

from agents.harness.models import HarnessSpec


def load_harness_spec(path: Path) -> HarnessSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid harness YAML: {path}")
    return HarnessSpec.model_validate(raw)
