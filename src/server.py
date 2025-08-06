# boot-python/src/server.py
import logging
import os
from pathlib import Path

import toml

# Import the generated protobuf files.
# Note: These will show as errors until we compile the .proto file.
from .generated import plugin_pb2, plugin_pb2_grpc


def get_prompts_path() -> Path:
    """
    Finds the absolute path to the 'prompts' directory.

    This function is robust enough to work whether the plugin is run from the
    development environment (e.g., `poetry run boot-python`) or as an installed
    package. It looks for the 'prompts' directory relative to this file.

    Returns:
        A Path object pointing to the 'prompts' directory.

    Raises:
        FileNotFoundError: If the 'prompts' directory cannot be found.
    """
    # The path to this current file (__file__)
    current_file_path = Path(__file__).resolve()
    # The 'src' directory
    src_dir = current_file_path.parent
    # The project root directory (one level up from 'src')
    project_root = src_dir.parent
    prompts_path = project_root / "prompts"

    if not prompts_path.is_dir():
        raise FileNotFoundError(f"Could not find 'prompts' directory at {prompts_path}")
    return prompts_path


def format_spec_for_prompt(spec_toml_content: str) -> str:
    """
    Parses the raw TOML content from the user's spec and formats it
    into a string for inclusion in the final prompt.

    Args:
        spec_toml_content: The raw string content of the spec.toml file.

    Returns:
        A formatted string summarizing the user's request.
    """
    try:
        spec = toml.loads(spec_toml_content)
        description = spec.get("description", "No description provided.")
        project_name = spec.get("project", {}).get("name", "Unnamed project")
        return f"--- USER SPECIFICATION ---\nProject Name: {project_name}\nDescription: {description}"
    except toml.TomlDecodeError as e:
        logging.error(f"Failed to parse TOML: {e}")
        return "--- USER SPECIFICATION ---\nError: Invalid TOML format provided."


class BootCodePluginServicer(plugin_pb2_grpc.BootCodePluginServicer):
    """
    Implements the gRPC service for the Python plugin.

    This class contains the logic that runs when the core application calls
    the `GetPromptComponents` RPC.
    """

    def GetPromptComponents(self, request, context):
        """
        Handles the incoming gRPC request from the core application.
        """
        spec_content = request.spec_toml_content
        components = {}

        try:
            prompts_dir = get_prompts_path()
            for entry in os.scandir(prompts_dir):
                if entry.is_file():
                    file_path = Path(entry.path)
                    components[file_path.name] = file_path.read_text()

            user_spec_prompt = format_spec_for_prompt(spec_content)

            return plugin_pb2.GetPromptComponentsResponse(
                components=components, user_spec_prompt=user_spec_prompt
            )
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            # Set an error status for the gRPC response
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"An internal error occurred: {e}")
            return plugin_pb2.GetPromptComponentsResponse()
