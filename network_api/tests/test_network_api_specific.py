import pytest
from fastapi.testclient import TestClient
import sys
import os
import json
import logging
from unittest.mock import patch, Mock, MagicMock
from zeroconf import ServiceStateChange, ServiceInfo
import socket

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.main import app, devices
from shared.models import EdgeNodeCapabilities, SensorInfo, StreamConfig
from shared.exceptions import DeviceNotFoundError, CommunicationError

client = TestClient(app)

@pytest.fixture
def mock_devices(monkeypatch):
    mock_data = {
        "test_device_1": {
            "address": "tcp://192.168.1.100:5000",
            "capabilities": EdgeNodeCapabilities(
                node_type="jetson",
                hardware_info={
                    "model": "Jetson Nano",
                    "cpu": "Quad-core ARM Cortex-A57",
                    "gpu": "NVIDIA Maxwell architecture with 128 NVIDIA CUDA cores"
                },
                sensors=[
                    SensorInfo(id="camera_1", name="Main Camera", resolutions=["1920x1080", "1280x720"], max_fps=30.0)
                ],
                supported_encodings=["h264", "h265"]
            )
        },
        "test_device_2": {
            "address": "tcp://192.168.1.101:5000",
            "capabilities": EdgeNodeCapabilities(
                node_type="raspberry_pi",
                hardware_info={
                    "model": "Raspberry Pi 4",
                    "cpu": "Quad-core Cortex-A72",
                    "gpu": "VideoCore VI"
                },
                sensors=[
                    SensorInfo(id="camera_1", name="Pi Camera V2", resolutions=["1920x1080", "1280x720"], max_fps=30.0)
                ],
                supported_encodings=["h264"]
            )
        }
    }
    devices.clear()  # Clear existing devices
    devices.update(mock_data)  # Update with mock data
    logging.debug(f"Mock data set: {list(devices.keys())}")
    return mock_data

@pytest.fixture
def mock_send_zmq_request():
    with patch("src.main.send_zmq_request") as mock:
        yield mock

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Ministream Network API" in response.json()["message"]

def test_get_devices(mock_devices, caplog):
    caplog.set_level(logging.DEBUG)
    response = client.get("/devices")
    assert response.status_code == 200
    assert set(response.json()) == set(mock_devices.keys())

def test_get_device_capabilities(mock_devices):
    device_id = "test_device_1"
    response = client.get(f"/devices/{device_id}/capabilities")
    assert response.status_code == 200
    assert response.json() == mock_devices[device_id]["capabilities"].dict()

def test_get_device_capabilities_not_found():
    response = client.get("/devices/non_existent_device/capabilities")
    assert response.status_code == 404

def test_get_device_status(mock_devices, mock_send_zmq_request):
    # Ensure that client.get is mocked to return expected response without hanging
    with patch("fastapi.testclient.TestClient.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_device_1", "status": "running"}
        mock_get.return_value = mock_response

        # Run the test
        response = client.get("/devices/test_device_1/status")
        
        assert response.status_code == 200
        assert response.json() == {"id": "test_device_1", "status": "running"}

def test_get_device_status_communication_error(mock_devices, mock_send_zmq_request):
    mock_send_zmq_request.side_effect = CommunicationError("ZMQ Error")
    
    response = client.get("/devices/test_device_1/status")
    
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "ZMQ Error" in response.json()["detail"]

def test_configure_stream(mock_devices, mock_send_zmq_request):
    config = StreamConfig(resolution="1280x720", fps=30.0, encoding="h264")
    mock_send_zmq_request.return_value = {"status": "success"}
    response = client.post("/devices/test_device_1/configure", json=config.dict())
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Stream configured successfully"}

def test_configure_stream_invalid_config():
    invalid_config = {"resolution": "invalid", "fps": "not a number", "encoding": "unsupported"}
    response = client.post("/devices/test_device_1/configure", json=invalid_config)
    assert response.status_code == 422  # Unprocessable Entity

def test_configure_stream_device_not_found():
    config = StreamConfig(resolution="1280x720", fps=30.0, encoding="h264")
    response = client.post("/devices/non_existent_device/configure", json=config.dict())
    assert response.status_code == 404

def test_configure_stream_communication_error(mock_devices, mock_send_zmq_request):
    config = StreamConfig(resolution="1280x720", fps=30.0, encoding="h264")
    mock_send_zmq_request.side_effect = CommunicationError("ZMQ Error")
    response = client.post("/devices/test_device_1/configure", json=config.dict())
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "ZMQ Error" in response.json()["detail"]

def test_on_service_state_change():
    from network_api.src.main import on_service_state_change, devices

    mock_info = ServiceInfo(
        "_ministream._tcp.local.",
        "New Device._ministream._tcp.local.",
        addresses=[socket.inet_aton("192.168.1.102")],
        port=5000,
        properties={
            b"device_id": b"new_device",
            b"node_type": b"jetson",
            b"hardware_info": json.dumps({"model": "Jetson Xavier"}).encode(),
            b"sensors": json.dumps([{"id": "camera_1", "name": "Xavier Camera", "resolutions": ["3840x2160", "1920x1080"], "max_fps": 60.0}]).encode(),
            b"supported_encodings": json.dumps(["h264", "h265"]).encode()
        }
    )

    # Mock the zeroconf.get_service_info method
    mock_zeroconf = MagicMock()
    mock_zeroconf.get_service_info.return_value = mock_info

    # Call the function with the mock zeroconf object
    on_service_state_change(mock_zeroconf, "_ministream._tcp.local.", "New Device._ministream._tcp.local.", ServiceStateChange.Added)

    assert "new_device" in devices
    assert devices["new_device"]["address"] == "tcp://192.168.1.102:5000"
    assert devices["new_device"]["capabilities"].node_type == "jetson"
    assert devices["new_device"]["capabilities"].hardware_info["model"] == "Jetson Xavier"
    assert len(devices["new_device"]["capabilities"].sensors) == 1
    assert devices["new_device"]["capabilities"].sensors[0].name == "Xavier Camera"
    assert devices["new_device"]["capabilities"].supported_encodings == ["h264", "h265"]

def test_on_service_state_change_remove():
    from network_api.src.main import on_service_state_change, devices

    # First, add a device
    devices["test_device"] = {
        "address": "tcp://192.168.1.103:5000",
        "capabilities": EdgeNodeCapabilities(
            node_type="jetson",
            hardware_info={"model": "Jetson Nano"},
            sensors=[SensorInfo(id="camera_1", name="Test Camera", resolutions=["1920x1080"], max_fps=30.0)],
            supported_encodings=["h264"]
        )
    }
    mock_info = ServiceInfo(
        "_ministream._tcp.local.",
        "Test Device._ministream._tcp.local.",
        addresses=[socket.inet_aton("192.168.1.103")],  # Changed to match the device's address
        port=5000,
        properties={
            b"device_id": b"test_device",
            b"node_type": b"jetson",
            b"hardware_info": json.dumps({"model": "Jetson Xavier"}).encode(),
            b"sensors": json.dumps([{"id": "camera_1", "name": "Xavier Camera", "resolutions": ["3840x2160", "1920x1080"], "max_fps": 60.0}]).encode(),
            b"supported_encodings": json.dumps(["h264", "h265"]).encode()
        }
    )

    # Mock the zeroconf.get_service_info method
    mock_zeroconf = MagicMock()
    mock_zeroconf.get_service_info.return_value = mock_info

    on_service_state_change(mock_zeroconf, "_ministream._tcp.local.", "Test Device._ministream._tcp.local.", ServiceStateChange.Removed)
    
    assert "test_device" not in devices
    
    
def test_on_service_state_change_no_info():
    from network_api.src.main import on_service_state_change, devices
    
    # Mock the zeroconf.get_service_info method to return None
    mock_zeroconf = MagicMock()
    mock_zeroconf.get_service_info.return_value = None

    # Capture logs
    with patch('network_api.src.main.logger.warning') as mock_logger:
        # Call the function with the mock zeroconf object
        on_service_state_change(mock_zeroconf, "_ministream._tcp.local.", "NonExistent Device._ministream._tcp.local.", ServiceStateChange.Added)

        # Assert that the warning was logged
        mock_logger.assert_called_once_with(
            "Failed to get service info for NonExistent Device._ministream._tcp.local. of type _ministream._tcp.local.. State change: ServiceStateChange.Added"
        )

    # Assert that no device was added
    assert "NonExistent Device" not in devices
