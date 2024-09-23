import pytest
from fastapi.testclient import TestClient
from network_api.src.main import app, devices
from shared.models import EdgeNodeCapabilities, SensorInfo

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
        }
    }
    monkeypatch.setattr("network_api.src.api.devices", mock_data)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Ministream Network API" in response.json()["message"]

def test_get_devices(mock_devices):
    response = client.get("/devices")
    assert response.status_code == 200
    assert "test_device_1" in response.json()

def test_get_device_status(mock_devices):
    # This test assumes you have implemented the get_device_status endpoint
    response = client.get("/devices/test_device_1/status")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "status" in response.json()

def test_get_device_status_not_found(mock_devices):
    response = client.get("/devices/non_existent_device/status")
    assert response.status_code == 404

def test_on_service_state_change():
    # This test simulates the addition of a new device through Zeroconf
    from network_api.src.main import on_service_state_change
    from zeroconf import ServiceStateChange
    import socket

    class MockServiceInfo:
        def __init__(self):
            self.addresses = [socket.inet_aton("192.168.1.101")]
            self.port = 5000
            self.properties = {
                b"device_id": b"new_device",
                b"capabilities": b'{"node_type": "jetson", "hardware_info": {}, "sensors": [], "supported_encodings": []}'
            }

    on_service_state_change(None, "_ministream._tcp.local.", "New Device", ServiceStateChange.Added)
    
    assert "new_device" in devices
    assert devices["new_device"]["address"] == "tcp://192.168.1.101:5000"

