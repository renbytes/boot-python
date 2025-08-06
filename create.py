# create_python_plugin.py
import os
from pathlib import Path

# --- Configuration ---
PLUGIN_NAME = "boot-python"
DIRECTORIES = [
    "prompts",
    "src",
    "src/generated",
    "proto",
]
FILES = {
    ".gitignore": """
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.venv/
env/
venv/

# gRPC / Protobuf
src/generated/

# Distribution / packaging
dist/
build/
eggs/
*.egg-info/
*.egg

# Logs
*.log
boot_debug.log
""",
    "pyproject.toml": """
[tool.poetry]
name = "boot-python"
version = "0.1.0"
description = "A prompt-provider plugin for generating Python projects with boot-code."
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.9"
grpcio = "^1.60.0"
protobuf = "^4.25.0"
grpcio-tools = "^1.60.0"
toml = "^0.10.2"
# Add other dependencies as needed, e.g., for spec parsing

[tool.poetry.scripts]
boot-python = "src.main:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
""",
    "README.md": """
# boot-python

A "Prompt Provider" plugin for **boot-code**.

This Python application is a lightweight gRPC server that serves language-specific prompt components to `boot-code`. Its sole responsibility is to provide the building blocks that the core application uses to construct high-quality prompts for generating Python code.
""",
    "proto/plugin.proto": """
// proto/plugin.proto
syntax = "proto3";
package plugin;

service BootCodePlugin {
  rpc GetPromptComponents(GetPromptComponentsRequest) returns (GetPromptComponentsResponse) {}
}

message GetPromptComponentsRequest {
  string spec_toml_content = 1;
}

message GetPromptComponentsResponse {
  // A map to hold all prompt files, keyed by their filename.
  map<string, string> components = 1;
  // The user-specific prompt is kept separate as it's generated from the request.
  string user_spec_prompt = 2;
}
""",
    "src/__init__.py": "",
    "src/generated/__init__.py": "",
    "src/main.py": "",
    "src/server.py": "",
    "prompts/base_instructions.txt": "",
    "prompts/language_rules.txt": "",
    "prompts/review_instructions.txt": "",
    "prompts/Makefile": "",
}

# --- Main Logic ---
def create_project_structure():
    """Creates the directories and files for the new plugin."""
    root = Path(PLUGIN_NAME)
    if root.exists():
        print(f"Directory '{PLUGIN_NAME}' already exists. Aborting.")
        return

    print(f"Creating project structure for '{PLUGIN_NAME}'...")
    root.mkdir()

    for directory in DIRECTORIES:
        (root / directory).mkdir(parents=True)

    for file_path, content in FILES.items():
        (root / file_path).write_text(content.strip())

    print("✅ Project structure created successfully.")
    print(f"\nNext steps:")
    print(f"  1. cd {PLUGIN_NAME}")
    print(f"  2. poetry install")
    print(f"  3. poetry run python -m grpc_tools.protoc -I./proto --python_out=./src/generated --grpc_python_out=./src/generated ./proto/plugin.proto")


if __name__ == "__main__":
    create_project_structure()
