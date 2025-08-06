# boot-python/src/main.py
import logging
import sys
from concurrent import futures

import grpc

# Import the generated protobuf files and the server implementation
# Note: These will show as errors until we compile the .proto file
from .generated import plugin_pb2, plugin_pb2_grpc
from .server import BootCodePluginServicer


def serve():
    """
    Starts the gRPC server, performs the handshake, and waits for requests.

    This function is the core of the plugin's execution. It follows a strict
    protocol required by the `boot-code` core application:

    1.  **Handshake to stdout**: It prints a single, specially formatted line to
        standard output (stdout). `boot-code` reads this line to know which
        port to connect to.
    2.  **Logging to stderr**: All other output, including logs and errors,
        is directed to standard error (stderr). This keeps stdout clean for the
        handshake.
    """
    # Configure logging to go to stderr
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    # Create a gRPC server with a thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Attach the servicer (the actual request-handling logic) to the server
    plugin_pb2_grpc.add_BootCodePluginServicer_to_server(
        BootCodePluginServicer(), server
    )

    # Bind the server to an available port on the local machine.
    # Port 0 tells the OS to assign an ephemeral (randomly available) port.
    port = server.add_insecure_port("127.0.0.1:0")

    # --- The Handshake ---
    # Print the connection information to stdout for the core application to read.
    # The format "1|1|tcp|HOST:PORT|grpc" is a required contract.
    print(f"1|1|tcp|127.0.0.1:{port}|grpc", flush=True)

    try:
        server.start()
        logging.info(f"Plugin server started on 127.0.0.1:{port}")
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("Server shutting down.")
        server.stop(0)


def main():
    """
    Entry point function defined in pyproject.toml.
    """
    serve()


if __name__ == "__main__":
    main()
