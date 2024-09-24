import uuid
from .base_hal import BaseHAL
from shared.models import StreamConfig, EdgeNodeCapabilities, SensorInfo
from shared.exceptions import StreamError, SensorError
from shared.logger import edge_node_logger as logger

class MockJetsonHAL(BaseHAL):
    """
    A mock implementation of the Hardware Abstraction Layer (HAL) for Jetson devices.
    This class simulates the behavior of a Jetson device for testing and development purposes.
    """

    def __init__(self):
        """
        Initialize the MockJetsonHAL.
        Generates a unique device ID and initializes the pipeline to None.
        """
        super().__init__()
        self.device_id = str(uuid.uuid4())
        self.pipeline = None

    def detect_sensors(self):
        """
        Simulate the detection of sensors on the mock Jetson device.

        Returns:
            list: A list containing a single SensorInfo object representing a mock camera.

        Raises:
            SensorError: If there's an error detecting sensors (simulated).
        """
        try:
            return [
                SensorInfo(
                    id="mock_camera_0",
                    name="Mock Jetson Camera",
                    resolutions=["640x480", "1280x720", "1920x1080"],
                    max_fps=30.0
                )
            ]
        except Exception as e:
            logger.error(f"Error detecting mock sensors: {str(e)}")
            raise SensorError(f"Error detecting mock sensors: {str(e)}")

    def start_stream(self, config: StreamConfig):
        """
        Simulate starting a video stream with the given configuration.

        Args:
            config (StreamConfig): Configuration for the stream.

        Raises:
            StreamError: If there's an error starting the stream (simulated).
        """
        try:
            logger.info(f"Starting mock stream with config: {config}")
            self.pipeline = "Mock GStreamer pipeline"
        except Exception as e:
            logger.error(f"Error starting mock stream: {str(e)}")
            raise StreamError(f"Error starting mock stream: {str(e)}")

    def stop_stream(self):
        """
        Simulate stopping the current video stream.
        """
        logger.info("Stopping mock stream")
        self.pipeline = None

    def get_frame(self):
        """
        Simulate capturing a frame from the video stream.

        Returns:
            bytes: A mock frame data.

        Raises:
            StreamError: If there's an error capturing the frame (simulated).
        """
        try:
            return b"Mock frame data"
        except Exception as e:
            logger.error(f"Error capturing mock frame: {str(e)}")
            raise StreamError(f"Error capturing mock frame: {str(e)}")

    def adjust_settings(self, settings):
        """
        Simulate adjusting camera settings.

        Args:
            settings (dict): A dictionary of settings to adjust.
        """
        print(f"Adjusting mock settings: {settings}")

    def get_capabilities(self):
        """
        Get the simulated capabilities of the mock Jetson device.

        Returns:
            EdgeNodeCapabilities: An object containing the mock device's capabilities.
        """
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

    def __del__(self):
        """
        Destructor for the MockJetsonHAL class.
        Ensures that the mock stream is stopped when the object is destroyed.
        """
        self.stop_stream()
        logger.info("Mock Jetson HAL destroyed")
