from .base_hal import BaseHAL
from shared.models import StreamConfig, EdgeNodeCapabilities, SensorInfo
import Jetson.GPIO as GPIO
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from zeroconf import ServiceInfo, Zeroconf
import socket
import uuid

class JetsonHAL(BaseHAL):
    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.device_id = str(uuid.uuid4())
        self.zeroconf = Zeroconf()
        Gst.init(None)

    def detect_sensors(self):
        # Sensor detection logic remains the same
        return [{
            "id": "jetson_camera_0",
            "name": "Jetson Onboard Camera",
            "resolutions": ["640x480", "1280x720", "1920x1080"],
            "max_fps": 30.0
        }]

    def start_stream(self, config):
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

    def stop_stream(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None

    def adjust_settings(self, settings):
        # Implement camera settings adjustment using GStreamer if needed
        pass

    def get_capabilities(self) -> EdgeNodeCapabilities:
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

    def __del__(self):
        self.stop_stream()
        self.zeroconf.close()
