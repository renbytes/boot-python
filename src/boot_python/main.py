import logging
import os
import signal
import socket
import sys
import time
from concurrent import futures

import grpc

from boot_python.generated import plugin_pb2_grpc
from boot_python.server import BootPluginServicer

# All logs -> STDERR; keep STDOUT pristine for handshake
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(message)s")


def _pick_loopback_port() -> tuple[str, int]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    host, port = s.getsockname()
    s.close()
    return host, port


def main() -> None:
    # Start gRPC server
    host, port = _pick_loopback_port()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    plugin_pb2_grpc.add_BootCodePluginServicer_to_server(BootPluginServicer(), server)
    server.add_insecure_port(f"{host}:{port}")

    # Print handshake to STDOUT only (no extra whitespace/newlines!)
    # Format: 1|1|tcp|HOST:PORT|grpc
    print(f"1|1|tcp|{host}:{port}|grpc", end="", flush=True)

    server.start()
    logging.info("boot-python started on %s:%d", host, port)
    
   # Test fast-exit: if set, skip the blocking loop so imports/patches won't hang.
    if os.environ.get("BOOT_PYTHON_TEST_EXIT_AFTER_HANDSHAKE") == "1":
        logging.info("Exiting immediately due to BOOT_PYTHON_TEST_EXIT_AFTER_HANDSHAKE=1")
        server.stop(grace=None)
        logging.info("boot-python stopped")
        return

    # Graceful shutdown
    stop_event = {"stop": False}

    def _sigterm(_sig, _frm):
        logging.info("Received shutdown signal")
        stop_event["stop"] = True
        server.stop(grace=None)

    signal.signal(signal.SIGINT, _sigterm)
    signal.signal(signal.SIGTERM, _sigterm)

    try:
        while not stop_event["stop"]:
            time.sleep(0.2)
    finally:
        logging.info("boot-python stopped")


if __name__ == "__main__":
    main()
