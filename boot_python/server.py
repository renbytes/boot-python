from __future__ import annotations

import logging
from importlib import resources as ir
from typing import Dict

import grpc

from boot_python.generated import plugin_pb2, plugin_pb2_grpc

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # Python ≤3.10
    import tomli as tomllib  # type: ignore[no-redef]

PROMPTS_PKG = "boot_python.prompts"


def _load_prompts() -> Dict[str, str]:
    files = {}
    try:
        # Iterate package resources
        for entry in ir.files(PROMPTS_PKG).iterdir():
            if entry.is_file() and entry.name.endswith(".txt"):
                files[entry.name] = entry.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        logging.warning("Failed to load prompts: %s", e)
    return files


def _derive_user_spec_prompt(spec_toml: str) -> str:
    if not spec_toml:
        return "User requests a python project. Description: (unavailable)"
    try:
        data = tomllib.loads(spec_toml)
        project = data.get("project", {}) if isinstance(data, dict) else {}
        name = project.get("name", "(unknown)")
        lang = project.get("language", "python")
        descr = project.get("description", "")
        return f"User requests a {lang} project named '{name}'. Description: {descr}"
    except Exception as e:  # noqa: BLE001
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