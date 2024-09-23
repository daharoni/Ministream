import sys
import os
import pytest

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from edge_node.src.hardware_abstraction.mock_jetson_hal import MockJetsonHAL as HAL
from shared.models import StreamConfig, SensorInfo

@pytest.fixture
def jetson_hal():
    return HAL()

def test_jetson_hal_initialization(jetson_hal):
    assert jetson_hal.device_id is not None
    assert jetson_hal.pipeline is None

def test_jetson_hal_detect_sensors(jetson_hal):
    sensors = jetson_hal.detect_sensors()
    assert len(sensors) > 0
    assert isinstance(sensors[0], SensorInfo)
    assert sensors[0].id is not None
    assert sensors[0].name is not None
    assert isinstance(sensors[0].resolutions, list)
    assert sensors[0].max_fps is not None

def test_jetson_hal_start_stream(jetson_hal):
    config = StreamConfig(resolution="1280x720", fps=30.0, encoding="h264")
    jetson_hal.start_stream(config)
    assert jetson_hal.pipeline is not None

def test_jetson_hal_stop_stream(jetson_hal):
    config = StreamConfig(resolution="1280x720", fps=30.0, encoding="h264")
    jetson_hal.start_stream(config)
    jetson_hal.stop_stream()
    assert jetson_hal.pipeline is None

def test_jetson_hal_get_capabilities(jetson_hal):
    capabilities = jetson_hal.get_capabilities()
    assert capabilities.node_type == "jetson"
    assert "model" in capabilities.hardware_info
    assert len(capabilities.sensors) > 0
    assert len(capabilities.supported_encodings) > 0
