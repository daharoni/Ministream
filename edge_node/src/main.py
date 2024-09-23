import asyncio
import os
import json
from hardware_abstraction.jetson_hal import JetsonHAL
from sensor_manager import SensorManager
from controller import Controller
from config import load_config

async def main():
    # Get the config path from an environment variable, with a default
    config_path = os.environ.get('MINISTREAM_CONFIG', 'configs/jetson_nano/config_1080p.yaml')
    config = load_config(config_path)
    hal = JetsonHAL(config["device"], config["camera"], config["gstreamer"])
    sensor_manager = SensorManager(hal)
    controller = Controller(sensor_manager, hal, config["zmq"])

    # Register the service for discovery with capabilities
    capabilities = hal.get_capabilities()
    info = ServiceInfo(
        "_ministream._tcp.local.",
        f"Jetson_{hal.device_id}._ministream._tcp.local.",
        addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
        port=config["network"]["discovery_port"],
        properties={
            "device_id": hal.device_id,
            "capabilities": json.dumps(capabilities.dict())
        }
    )
    zeroconf = Zeroconf()
    zeroconf.register_service(info)

    await asyncio.gather(
        sensor_manager.run(),
        controller.run()
    )

    zeroconf.close()

if __name__ == "__main__":
    asyncio.run(main())
