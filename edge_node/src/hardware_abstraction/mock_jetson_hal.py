import uuid
from .base_hal import BaseHAL
from shared.models import StreamConfig, EdgeNodeCapabilities, SensorInfo

class MockJetsonHAL(BaseHAL):
    def __init__(self):
        super().__init__()
        self.device_id = str(uuid.uuid4())
        self.pipeline = None

    def detect_sensors(self):
        return [
            SensorInfo(
                id="mock_camera_0",
                name="Mock Jetson Camera",
                resolutions=["640x480", "1280x720", "1920x1080"],
                max_fps=30.0
            )
        ]

    def start_stream(self, config: StreamConfig):
        print(f"Starting mock stream with config: {config}")
        self.pipeline = "Mock GStreamer pipeline"

    def stop_stream(self):
        print("Stopping mock stream")
        self.pipeline = None

    def get_frame(self):
        return b"Mock frame data"

    def adjust_settings(self, settings):
        print(f"Adjusting mock settings: {settings}")

    def get_capabilities(self):
        return EdgeNodeCapabilities(
            node_type="jetson",
            hardware_info={
                "model": "Mock Jetson Nano",
                "cpu": "Mock CPU",
                "gpu": "Mock GPU"
            },
            sensors=[
                SensorInfo(
                    id="mock_camera_0",
                    name="Mock Jetson Camera",
                    resolutions=["640x480", "1280x720", "1920x1080"],
                    max_fps=30.0
                )
            ],
            supported_encodings=["h264", "h265"]
        )
