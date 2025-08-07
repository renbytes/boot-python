import logging
import os
from unittest.mock import patch

def test_handshake_and_logging(capsys, caplog, monkeypatch):
    # Arrange: make main exit immediately after handshake (no blocking loop)
    monkeypatch.setenv("BOOT_PYTHON_TEST_EXIT_AFTER_HANDSHAKE", "1")

    with patch("boot_python.main._pick_loopback_port", return_value=("127.0.0.1", 54321)), \
         patch("boot_python.main.grpc.server") as mock_grpc_server, \
         patch("boot_python.main.plugin_pb2_grpc") as mock_pb2_grpc, \
         patch("boot_python.main.BootPluginServicer") as mock_servicer, \
         caplog.at_level(logging.INFO):

        # Import here (after patches/env) so collection doesn't trigger side effects
        from boot_python.main import main as entry_main

        server_instance = mock_grpc_server.return_value
        server_instance.add_insecure_port.return_value = 54321

        # Act
        entry_main()

    # Assert stdout handshake
    out, _ = capsys.readouterr()
    assert out == "1|1|tcp|127.0.0.1:54321|grpc"

    # Assert logging to stderr
    assert "boot-python started on 127.0.0.1:54321" in caplog.text
    assert "Exiting immediately due to BOOT_PYTHON_TEST_EXIT_AFTER_HANDSHAKE=1" in caplog.text
    assert "boot-python stopped" in caplog.text

    # Wiring
    mock_pb2_grpc.add_BootCodePluginServicer_to_server.assert_called_once_with(
        mock_servicer.return_value, mock_grpc_server.return_value
    )
    server_instance.add_insecure_port.assert_called_once_with("127.0.0.1:54321")
    server_instance.start.assert_called_once()
    server_instance.stop.assert_called_once()


def test_grpc_server_setup(monkeypatch):
    monkeypatch.setenv("BOOT_PYTHON_TEST_EXIT_AFTER_HANDSHAKE", "1")

    with patch("boot_python.main._pick_loopback_port", return_value=("127.0.0.1", 12345)), \
         patch("boot_python.main.grpc.server") as mock_grpc_server, \
         patch("boot_python.main.plugin_pb2_grpc") as mock_pb2_grpc, \
         patch("boot_python.main.BootPluginServicer") as mock_servicer:

        from boot_python.main import main as entry_main
        server_instance = mock_grpc_server.return_value

        entry_main()

    mock_pb2_grpc.add_BootCodePluginServicer_to_server.assert_called_once_with(
        mock_servicer.return_value, server_instance
    )
    server_instance.add_insecure_port.assert_called_once_with("127.0.0.1:12345")
    server_instance.start.assert_called_once()
    server_instance.stop.assert_called_once()
