import pytest
import logging
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_api.src.main import app
from shared.models import EdgeNodeCapabilities, SensorInfo, StreamConfig

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler and set its level to INFO
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the formatter to the console handler
ch.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(ch)

client = TestClient(app)

# Set up logging
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def setup_logging(caplog):
    caplog.set_level(logging.INFO)

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
    monkeypatch.setattr("network_api.src.main.devices", mock_data)

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

def test_configure_stream(mock_devices, monkeypatch):
    logger.info("Starting test_configure_stream")
    config = StreamConfig(resolution="1280x720", fps=30.0, encoding="h264")
    logger.info(f"Created StreamConfig: {config}")
    
    # Mock the send_zmq_request function to return immediately
    async def mock_send_zmq_request(address, message):
        return {"status": "success"}
    
    monkeypatch.setattr("network_api.src.main.send_zmq_request", mock_send_zmq_request)
    
    logger.info("Attempting to send POST request")
    response = client.post("/devices/test_device_1/configure", json=config.dict(), timeout=5)
    logger.info(f"Received response")
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response content: {response.content}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    logger.info("Test completed successfully")

def test_configure_stream_invalid_device(mock_devices):
    config = StreamConfig(resolution="1280x720", fps=30.0, encoding="h264")
    response = client.post("/devices/non_existent_device/configure", json=config.dict())
    assert response.status_code == 404
