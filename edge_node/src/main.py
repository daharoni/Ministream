import asyncio
import os
import json
import uuid
from edge_node.src.sensor_manager import SensorManager
from edge_node.src.controller import Controller
from edge_node.src.config import load_config
from edge_node.src.streamer import Streamer  # Import the Streamer class
from zeroconf.asyncio import AsyncZeroconf
from zeroconf import ServiceInfo
import socket
from shared.logger import edge_node_logger as logger
import aiohttp

# Determine which HAL to use based on the environment
USE_MOCK = os.environ.get('USE_MOCK_HAL', 'true').lower() == 'true'

if USE_MOCK:
    from edge_node.src.hardware_abstraction.mock_jetson_hal import MockJetsonHAL as HAL
else:
    from edge_node.src.hardware_abstraction.jetson_hal import JetsonHAL as HAL

async def send_heartbeat(device_id, api_url):
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.post(f"{api_url}/devices/{device_id}/heartbeat") as response:
                    if response.status == 200:
                        logger.debug(f"Heartbeat sent for device {device_id}")
                    else:
                        logger.warning(f"Failed to send heartbeat: {response.status}")
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
            await asyncio.sleep(5)  # Send heartbeat every 5 seconds

async def register_service(config):
    """
    Register the edge node service with Zeroconf for discovery.

    Args:
        config (dict): The configuration dictionary for the edge node.

    Returns:
        tuple: A tuple containing the Zeroconf instance and the registered ServiceInfo.
    """
    zeroconf = AsyncZeroconf()
    host_ip = socket.gethostbyname(socket.gethostname())
    
    device_id = config.get('device_id', str(uuid.uuid4()))
    
    capabilities = HAL().get_capabilities()
    properties = {
        b"device_id": device_id.encode('utf-8'),
        b"node_type": capabilities.node_type.encode('utf-8'),
        b"hardware_info": json.dumps(capabilities.hardware_info).encode('utf-8'),
        b"sensors": json.dumps([sensor.dict() for sensor in capabilities.sensors]).encode('utf-8'),
        b"supported_encodings": json.dumps(capabilities.supported_encodings).encode('utf-8')
    }
    
    info = ServiceInfo(
        "_ministream._tcp.local.",
        f"EdgeNode_{device_id}._ministream._tcp.local.",
        addresses=[socket.inet_aton(host_ip)],
        port=config.get('zmq', {}).get('port', 0),  # Using .get() with default value
        properties=properties
    )
    
    logger.debug(f"Registering service with properties: {properties}")
    
    await zeroconf.async_register_service(info)
    return zeroconf, info

async def register_device(device_id, api_url, capabilities):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{api_url}/devices", json={
                "device_id": device_id,
                "capabilities": capabilities.dict()
            }) as response:
                if response.status == 200:
                    logger.info(f"Device {device_id} registered successfully")
                else:
                    logger.error(f"Failed to register device: {response.status}")
        except Exception as e:
            logger.error(f"Error registering device: {e}")

async def main():
    """
    The main function that sets up and runs the edge node.
    """
    logger.info("Starting Edge Node")
    config = load_config()
    
    # Ensure device_id is in the config
    if 'device_id' not in config:
        config['device_id'] = str(uuid.uuid4())
        logger.info(f"Generated new device_id: {config['device_id']}")

    logger.info(f"Loaded configuration: {config}")

    hal = HAL()
    sensor_manager = SensorManager(hal)
    streamer = Streamer(hal, config)  # Create a Streamer instance
    controller = Controller(sensor_manager, streamer, config)  # Pass streamer to Controller

    zeroconf, info = await register_service(config)

    # Define api_url and device_id
    api_url = os.environ.get('API_URL', 'http://network_api:8000')  # Use the service name as the hostname
    device_id = config.get('device_id', str(uuid.uuid4()))

    # Start the heartbeat task
    heartbeat_task = asyncio.create_task(send_heartbeat(device_id, api_url))

    # Register the device
    await register_device(device_id, api_url, hal.get_capabilities())

    try:
        await asyncio.gather(
            sensor_manager.run(),
            streamer.run(),  # Run the streamer
            controller.run(),
            heartbeat_task  # Include the heartbeat task in the gather call
        )
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        await zeroconf.async_unregister_service(info)  # Changed to async_unregister_service
        await zeroconf.close()

if __name__ == "__main__":
    asyncio.run(main())
