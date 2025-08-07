.PHONY: proto run build install test clean

proto:
	poetry run python -m grpc_tools.protoc -I./proto \
	  --python_out=./src/boot_python/generated \
	  --grpc_python_out=./src/boot_python/generated \
	  ./proto/plugin.proto
	# Patch absolute import to relative so package imports work
	sed -i '' 's/^import plugin_pb2 as plugin__pb2/from . import plugin_pb2 as plugin__pb2/' \
	  src/boot_python/generated/plugin_pb2_grpc.py

run:
	poetry run boot-python 2>/dev/null | head -1

build: proto
	poetry build

install: build
	pipx install dist/boot_python-*.whl

test:
	poetry run pytest -q

clean:
	rm -rf dist build .pytest_cache .ruff_cache
