from __future__ import annotations

import io
import logging
import os
from pathlib import Path
from typing import Dict, Tuple

import grpc

try:
    import tomllib  # Py>=3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # Py<=3.10

from boot_python.generated import plugin_pb2, plugin_pb2_grpc

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


def _read_text(p: Path) -> str:
    with p.open("r", encoding="utf-8") as f:
        return f.read()


def _load_prompts() -> Dict[str, str]:
    files = ["base_instructions.txt", "language_rules.txt", "review_instructions.txt", "README.md.template"]
    components: Dict[str, str] = {}
    for name in files:
        fp = PROMPTS_DIR / name
        if fp.exists():
            components[name] = _read_text(fp)
        else:
            logging.warning("Prompt file missing: %s", fp)
    return components


def _derive_user_spec_prompt(spec_toml: str) -> str:
    """
    Minimal, safe TOML decode to craft a user-specific prompt.
    Keep it defensive: if TOML parse fails, fall back gracefully.
    """
    try:
        data = tomllib.loads(spec_toml)
        project = data.get("project", {})
        name = project.get("name", "unknown-project")
        descr = project.get("description", "")
        lang  = project.get("language", "python")
        return f"User requests a {lang} project named '{name}'. Description: {descr}"
    except Exception as e:  # don’t fail plugin on TOML issues
        logging.warning("Failed to parse spec TOML: %s", e)
        return "User requests a python project. Description: (unavailable)"


class BootPluginServicer(plugin_pb2_grpc.BootCodePluginServicer):
    def GetPromptComponents(
        self,
        request: plugin_pb2.GetPromptComponentsRequest,
        context: grpc.ServicerContext,
    ) -> plugin_pb2.GetPromptComponentsResponse:
        components = _load_prompts()
        user_spec_prompt = _derive_user_spec_prompt(request.spec_toml_content or "")
        return plugin_pb2.GetPromptComponentsResponse(
            components=components,
            user_spec_prompt=user_spec_prompt,
        )
