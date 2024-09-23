import pytest
from fastapi.testclient import TestClient
from network_api.src.api import app
from shared.models import EdgeNodeCapabilities, SensorInfo, StreamConfig

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

def test_get_devices(mock_devices):
    response = client.get("/devices")
    assert response.status_code == 200
    assert response.json() == ["test_device_1"]

def test_get_device_capabilities(mock_devices):
    response = client.get("/devices/test_device_1/capabilities")
    assert response.status_code == 200
    assert response.json()["node_type"] == "jetson"
    assert "Main Camera" in [sensor["name"] for sensor in response.json()["sensors"]]

def test_get_device_capabilities_not_found(mock_devices):
    response = client.get("/devices/non_existent_device/capabilities")
    assert response.status_code == 404

def test_configure_stream(mock_devices):
    config = StreamConfig(resolution="1280x720", fps=30.0, encoding="h264")
    response = client.post("/devices/test_device_1/configure", json=config.dict())
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_configure_stream_invalid_device(mock_devices):
    config = StreamConfig(resolution="1280x720", fps=30.0, encoding="h264")
    response = client.post("/devices/non_existent_device/configure", json=config.dict())
    assert response.status_code == 404
