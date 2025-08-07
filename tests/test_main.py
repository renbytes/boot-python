# tests/test_main.py
import logging
import sys
from unittest.mock import MagicMock, patch

# We only need to mock the top-level 'generated' module to prevent
# the initial ImportError during test discovery.
sys.modules['src.generated'] = MagicMock()

# Import the modules to be tested AFTER setting up the initial mock
from src.main import main, serve


@patch('src.main.BootCodePluginServicer')
@patch('src.main.grpc.server')
def test_serve_handshake_and_logging(mock_grpc_server, mock_servicer, capsys, caplog):
    """
    Tests that the server performs the handshake correctly to stdout
    and that logging messages are correctly sent to stderr.
    """
    # Arrange
    mock_server_instance = mock_grpc_server.return_value
    mock_server_instance.add_insecure_port.return_value = 54321
    mock_server_instance.wait_for_termination.side_effect = KeyboardInterrupt

    # Act
    with caplog.at_level(logging.INFO):
        serve()

    # Assert stdout (Handshake)
    captured_streams = capsys.readouterr()
    expected_handshake = "1|1|tcp|127.0.0.1:54321|grpc\n"
    assert captured_streams.out == expected_handshake

    # Assert stderr (Logging)
    assert "Plugin server started on 127.0.0.1:54321" in caplog.text
    assert "Server shutting down." in caplog.text


# FIX: Add a specific patch for the object being called.
@patch('src.main.plugin_pb2_grpc')
@patch('src.main.BootCodePluginServicer')
@patch('src.main.grpc.server')
def test_serve_grpc_server_setup(mock_grpc_server, mock_servicer, mock_plugin_grpc):
    """
    Tests that the gRPC server is initialized and configured correctly.
    """
    # Arrange
    mock_server_instance = mock_grpc_server.return_value
    mock_server_instance.add_insecure_port.return_value = 12345
    mock_server_instance.wait_for_termination.side_effect = KeyboardInterrupt

    # Act
    serve()

    # Assert
    mock_grpc_server.assert_called_once()
    mock_servicer.assert_called_once()

    # FIX: Assert the call on the new, correct mock object.
    mock_plugin_grpc.add_BootCodePluginServicer_to_server.assert_called_once_with(
        mock_servicer.return_value, mock_server_instance
    )
    mock_server_instance.add_insecure_port.assert_called_with("127.0.0.1:0")
    mock_server_instance.start.assert_called_once()
    mock_server_instance.wait_for_termination.assert_called_once()
    mock_server_instance.stop.assert_called_with(0)


def test_main_entry_point(mocker):
    """
    Tests that the main() entry point correctly calls the serve() function.
    """
    # Arrange
    serve_spy = mocker.patch('src.main.serve')

    # Act
    main()

    # Assert
    serve_spy.assert_called_once()