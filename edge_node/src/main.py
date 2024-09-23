import asyncio
import os
import json
from edge_node.src.sensor_manager import SensorManager  # Update this line
from edge_node.src.controller import Controller  # Make sure this import is correct too
from edge_node.src.config import load_config  # Update this import as well
from zeroconf.asyncio import AsyncZeroconf
from zeroconf import ServiceInfo
import socket

# Determine which HAL to use based on the environment
USE_MOCK = os.environ.get('USE_MOCK_HAL', 'true').lower() == 'true'

if USE_MOCK:
    from edge_node.src.hardware_abstraction.mock_jetson_hal import MockJetsonHAL
else:
    from edge_node.src.hardware_abstraction.jetson_hal import JetsonHAL

async def main():
    # Get the config path from an environment variable, with a default
    config_path = os.environ.get('MINISTREAM_CONFIG', 'configs/jetson_nano/config_1080p.yaml')
    config = load_config(config_path)
    
    # Use MockJetsonHAL in development environment, real JetsonHAL otherwise
    if USE_MOCK:
        hal = MockJetsonHAL()
    else:
        hal = JetsonHAL(config["device"], config["camera"], config["gstreamer"])
    
    sensor_manager = SensorManager(hal)
    
    # Ensure that config["zmq"] exists, if not, use an empty dict
    zmq_config = config.get("zmq", {})
    controller = Controller(sensor_manager, hal, zmq_config)

    # Register the service for discovery with capabilities
    capabilities = hal.get_capabilities()
    properties = {
        b"device_id": hal.device_id.encode('utf-8'),
        b"node_type": capabilities.node_type.encode('utf-8'),
        b"hardware_info": json.dumps(capabilities.hardware_info).encode('utf-8'),
        b"sensors": json.dumps([sensor.dict() for sensor in capabilities.sensors]).encode('utf-8'),
        b"supported_encodings": json.dumps(capabilities.supported_encodings).encode('utf-8')
    }
    
    info = ServiceInfo(
        "_ministream._tcp.local.",
        f"Jetson_{hal.device_id}._ministream._tcp.local.",
        addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
        port=config["network"]["discovery_port"],
        properties=properties
    )

    async with AsyncZeroconf() as aiozc:
        await aiozc.async_register_service(info)

        try:
            await asyncio.gather(
                sensor_manager.run(),
                controller.run()
            )
        finally:
            await aiozc.async_unregister_service(info)

if __name__ == "__main__":
    asyncio.run(main())
