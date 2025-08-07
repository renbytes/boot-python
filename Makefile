# Makefile for boot-python (packaged as src/boot_python)

.PHONY: help proto run build install reinstall uninstall test clean

PY        ?= poetry run python
PIPX      ?= pipx
PKG       := boot_python
GEN_DIR   := $(PKG)/generated
PROTO_IN  := proto/plugin.proto
WHEEL_GLOB:= dist/boot_python-*.whl

help:
	@echo "Targets:"
	@echo "  proto       Generate gRPC stubs into $(GEN_DIR) (with relative imports)"
	@echo "  run         Quick handshake smoke test"
	@echo "  build       Build wheel (runs proto first)"
	@echo "  install     pipx install the built wheel"
	@echo "  reinstall   pipx reinstall from the new wheel (uninstall if needed)"
	@echo "  uninstall   pipx uninstall boot-python"
	@echo "  test        Run pytest with fast-exit server flag"
	@echo "  clean       Remove build/test artifacts"

proto:
	poetry run python -m grpc_tools.protoc -I./proto \
	  --python_out=./boot_python/generated \
	  --grpc_python_out=./boot_python/generated \
	  ./proto/plugin.proto
	# Patch absolute import to relative so package imports work
	sed -i '' 's/^import plugin_pb2 as plugin__pb2/from . import plugin_pb2 as plugin__pb2/' \
	  boot_python/generated/plugin_pb2_grpc.py

run:
	@# Print the first line (handshake) only
	@poetry run boot-python 2>/dev/null | head -1

build: proto
	@poetry build

install: build
	@$(PIPX) install $(WHEEL_GLOB)

reinstall: build
	-@$(PIPX) uninstall boot-python >/dev/null 2>&1 || true
	@$(PIPX) install $(WHEEL_GLOB)

uninstall:
	@$(PIPX) uninstall boot-python

test:
	@BOOT_PYTHON_TEST_EXIT_AFTER_HANDSHAKE=1 poetry run pytest -q

clean:
	@rm -rf dist build .pytest_cache .ruff_cache
