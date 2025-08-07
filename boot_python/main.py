import argparse
import logging
import os
import signal
import sys
import time
from concurrent import futures

import grpc

from boot_python.generated import plugin_pb2_grpc
from boot_python.server import BootPluginServicer

# Send logs to STDERR so STDOUT stays clean for the handshake
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(message)s")

HANDSHAKE_PROTO = "1|1|tcp|{host}:{port}|grpc"
DEFAULT_HOST = "127.0.0.1"


def _bind_ephemeral_port(host: str = DEFAULT_HOST):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    plugin_pb2_grpc.add_BootCodePluginServicer_to_server(BootPluginServicer(), server)
    port = server.add_insecure_port(f"{host}:0")
    if not port:
        raise RuntimeError("Failed to bind gRPC port")
    server.start()
    return server, port


def _print_handshake(host: str, port: int) -> None:
    sys.stdout.write(HANDSHAKE_PROTO.format(host=host, port=port) + "\n")
    sys.stdout.flush()


def _run_server_until_signal(server: grpc.Server) -> None:
    stop = {"flag": False}

    def _sigterm(*_):
        stop["flag"] = True
        try:
            server.stop(grace=None)
        except Exception:
            pass

    signal.signal(signal.SIGINT, _sigterm)
    signal.signal(signal.SIGTERM, _sigterm)

    try:
        while not stop["flag"]:
            time.sleep(0.2)
    finally:
        logging.info("boot-python stopped")


def main() -> None:
    parser = argparse.ArgumentParser(prog="boot-python")
    parser.add_argument("--check", action="store_true", help="Print handshake and exit")
    args = parser.parse_args()

    server, port = _bind_ephemeral_port(DEFAULT_HOST)
    _print_handshake(DEFAULT_HOST, port)

    # For check/CI paths: stop and WAIT so the process fully exits
    if args.check or os.getenv("BOOT_PYTHON_TEST_EXIT_AFTER_HANDSHAKE"):
        fut = server.stop(0)  # immediate stop
        if fut is not None:
            fut.wait()
        return

    _run_server_until_signal(server)


if __name__ == "__main__":
    main()