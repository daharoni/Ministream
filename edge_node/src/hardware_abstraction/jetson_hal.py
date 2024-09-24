from .base_hal import BaseHAL
from shared.models import StreamConfig, EdgeNodeCapabilities, SensorInfo
import Jetson.GPIO as GPIO
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from zeroconf import ServiceInfo, Zeroconf
import socket
import uuid
from shared.exceptions import HardwareError, SensorError, StreamError
from shared.logger import edge_node_logger as logger

class JetsonHAL(BaseHAL):
    """
    Hardware Abstraction Layer (HAL) for Jetson devices.
    This class provides specific implementations for Jetson hardware,
    including sensor detection, stream management, and device capabilities.
    """

    def __init__(self):
        """
        Initialize the Jetson HAL.
        Sets up the GStreamer pipeline, generates a unique device ID,
        and initializes Zeroconf for service discovery.
        """
        super().__init__()
        self.pipeline = None
        self.device_id = str(uuid.uuid4())
        self.zeroconf = Zeroconf()
        Gst.init(None)
        logger.info("Jetson HAL initialized")

    def detect_sensors(self):
        """
        Detect available sensors on the Jetson device.

        Returns:
            list: A list of SensorInfo objects containing sensor information.

        Raises:
            SensorError: If there's an error detecting sensors.
        """
        try:
            # Note: This is a placeholder. In a real implementation,
            # you would need to actually detect the available cameras.
            return [SensorInfo(
                id="jetson_camera_0",
                name="Jetson Onboard Camera",
                resolutions=["640x480", "1280x720", "1920x1080"],
                max_fps=30.0
            )]
        except Exception as e:
            logger.error(f"Error detecting sensors: {str(e)}")
            raise SensorError(f"Error detecting sensors: {str(e)}")

    def start_stream(self, config):
        """
        Start a video stream with the given configuration.

        Args:
            config (StreamConfig): Configuration for the stream.

        Raises:
            StreamError: If there's an error starting the stream.
        """
        try:
            resolution = config.resolution
            fps = config.fps
            encoding = config.encoding

            pipeline_str = (
                f"v4l2src device=/dev/video0 ! video/x-raw,width={resolution.split('x')[0]},"
                f"height={resolution.split('x')[1]},framerate={fps}/1 ! tee name=t "
                f"t. ! queue ! {encoding}enc ! rtph264pay ! udpsink host=224.1.1.1 port=5000 "
                f"t. ! queue ! {encoding}enc ! mp4mux ! filesink location=/path/to/local/storage/video.mp4"
            )
            self.pipeline = Gst.parse_launch(pipeline_str)
            self.pipeline.set_state(Gst.State.PLAYING)

            # Register the service for discovery
            info = ServiceInfo(
                "_ministream._tcp.local.",
                f"Jetson_{self.device_id}._ministream._tcp.local.",
                addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
                port=5000,
                properties={"device_id": self.device_id}
            )
            self.zeroconf.register_service(info)
            logger.info(f"Stream started with config: {config}")
        except Exception as e:
            logger.error(f"Error starting stream: {str(e)}")
            raise StreamError(f"Error starting stream: {str(e)}")

    def stop_stream(self):
        """
        Stop the current video stream.
        """
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None
            logger.info("Stream stopped")

    def adjust_settings(self, settings):
        """
        Adjust camera settings.

        Args:
            settings (dict): A dictionary of settings to adjust.

        Note: This method is a placeholder and needs to be implemented.
        """
        # Implement camera settings adjustment using GStreamer if needed
        pass

    def get_capabilities(self) -> EdgeNodeCapabilities:
        """
        Get the capabilities of the Jetson device.

        Returns:
            EdgeNodeCapabilities: An object containing the device's capabilities.
        """
        return EdgeNodeCapabilities(
            node_type="jetson",
            hardware_info={
                "model": "Jetson Nano",
                "cpu": "Quad-core ARM Cortex-A57",
                "gpu": "NVIDIA Maxwell architecture with 128 NVIDIA CUDA cores"
            },
            sensors=self.detect_sensors(),
            supported_encodings=["h264", "h265"]
        )

    def get_frame(self):
        """
        Capture a frame from the video stream.

        Returns:
            bytes: The captured frame data.

        Raises:
            StreamError: If there's an error capturing the frame.
        """
        try:
            # Implement actual frame capture using GStreamer
            # This is a placeholder and needs to be implemented
            return b"Actual frame data"
        except Exception as e:
            logger.error(f"Error capturing frame: {str(e)}")
            raise StreamError(f"Error capturing frame: {str(e)}")

    def __del__(self):
        """
        Destructor for the JetsonHAL class.
        Ensures that the stream is stopped and Zeroconf is closed when the object is destroyed.
        """
        self.stop_stream()
        self.zeroconf.close()
        logger.info("Jetson HAL destroyed")
