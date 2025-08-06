# boot-python Developer Guide

This guide provides technical details for developing, testing, and troubleshooting the `boot-python` plugin.

## 1. Getting Started

**Prerequisites:**
* Python 3.9+
* Poetry

### Installation

1. **Clone the repository** and navigate into the directory.

2. **Install dependencies**: This command will create a virtual environment and install all necessary packages from `pyproject.toml`.

   ```bash
   poetry install
   ```

3. **Compile Protobufs**: The gRPC code is not checked into version control. You must generate it after installing the dependencies.

   ```bash
   poetry run python -m grpc_tools.protoc -I./proto --python_out=./src/generated --grpc_python_out=./src/generated ./proto/plugin.proto
   ```

> Note: `gRPC`'s generated files often incorrectly import using `import plugin_pb2 as plugin__pb2`, so should be manually switched to `from . import plugin_pb2 as plugin__pb2`

## 2. The Handshake Contract

`boot-code` discovers and communicates with plugins based on a simple, strict contract:

* **First line on `stdout`**: Must be the handshake string in the format `1|1|tcp|HOST:PORT|grpc`.
* **All other output**: All logs, warnings, and errors **must** be sent to `stderr`. This keeps `stdout` clean so the handshake is not corrupted. The `main.py` file is already configured to do this.

## 3. Testing the Plugin Locally

You can quickly test that the binary is producing the correct handshake and that logs are properly sent to `stderr`.

```bash
# From the boot-python project root, run the executable and grab the first line of stdout
poetry run boot-python 2>/dev/null | head -1
```

**Expected Output:**

```
1|1|tcp|127.0.0.1:<PORT>|grpc
```

*(The port number will be different each time)*

## 4. Debugging Plugin Discovery

`boot-code` discovers the plugin by finding an executable named `boot-python` on its `PATH`.

### Verify what `boot-code` Sees

From the `boot-code` directory, run this command to see which `boot-python` executable its environment will use:

```bash
poetry run which boot-python
```

If this command returns nothing, it means the `boot-python` executable is not in the `PATH` that the `boot-code` environment is using.

### How to Fix PATH Issues

The most common issue is that the plugin's virtual environment is not in your shell's `PATH`.

1. **Find the virtual environment's path** from within your `boot-python` directory:

   ```bash
   poetry env info --path
   ```

2. **Add the `bin` subdirectory** of that path to your shell's configuration file (e.g., `~/.zshrc` or `~/.bash_profile`).

   ```bash
   # Example for ~/.zshrc
   export PATH="/path/from/previous/command/bin:$PATH"
   ```

3. **Restart your terminal** for the changes to take effect.

## 5. Development Workflow

* **Format Code:**

  ```bash
  poetry run ruff format .
  ```

* **Lint Code:**

  ```bash
  poetry run ruff check . --fix
  ```

* **Run Unit Tests (if you add any):**

  ```bash
  poetry run pytest
  ```

## 6. Common `boot-code` Errors

* **`Plugin executable not found`**: This is a `PATH` issue. `boot-code` cannot find the `boot-python` binary. See the "How to Fix PATH Issues" section above.

* **`Invalid handshake` / `not enough values to unpack`**: This means the plugin wrote something to `stdout` before the handshake string. Ensure all logging and print statements in the Python code use `logging` or write to `sys.stderr`.

* **`ModuleNotFoundError`**: If the plugin fails with this error, it's likely an issue with relative vs. absolute imports within the plugin's `src` directory. Ensure all intra-package imports use the relative `.` syntax (e.g., `from .server import ...`).