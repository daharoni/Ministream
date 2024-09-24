from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import zmq
import asyncio
import json
from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
import socket
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from shared.models import SensorInfo, StreamConfig, DeviceStatus, EdgeNodeCapabilities
from shared.exceptions import DeviceNotFoundError, CommunicationError, APIError
from shared.logger import network_api_logger as logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    device_check_task = asyncio.create_task(periodic_device_check())
    yield
    device_check_task.cancel()
    await device_check_task

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dictionary to store information about discovered devices
devices = {}

import time

HEARTBEAT_TIMEOUT = 10  # Increase timeout to 30 seconds

def check_device_status():
    current_time = time.time()
    for device_id, device_info in list(devices.items()):
        if current_time - device_info.get('last_heartbeat', 0) > HEARTBEAT_TIMEOUT:
            logger.warning(f"Device {device_id} missed heartbeat")
            device_info['status'] = 'offline'
        else:
            device_info['status'] = 'online'

async def periodic_device_check():
    while True:
        check_device_status()
        await asyncio.sleep(5)  # Check every 5 seconds

def on_service_state_change(zeroconf, service_type, name, state_change):
    """
    Callback function for handling Zeroconf service state changes.
    
    Args:
        zeroconf (Zeroconf): The Zeroconf instance.
        service_type (str): The type of service.
        name (str): The name of the service.
        state_change (ServiceStateChange): The state change of the service.
    """
    logger.info(f"Service {name} of type {service_type} changed state to {state_change}")
    info = zeroconf.get_service_info(service_type, name)
    if not info:
        logger.warning(f"Failed to get service info for {name} of type {service_type}. State change: {state_change}")
        return

    if state_change is ServiceStateChange.Added:
        # Handle new device discovery
        info = zeroconf.get_service_info(service_type, name)
        if info:
            address = socket.inet_ntoa(info.addresses[0])
            port = info.port
            device_id = info.properties.get(b'device_id', b'').decode('utf-8')
            
            # Parse the capabilities
            node_type = info.properties.get(b'node_type', b'').decode('utf-8')
            hardware_info = json.loads(info.properties.get(b'hardware_info', b'{}').decode('utf-8'))
            sensors = json.loads(info.properties.get(b'sensors', b'[]').decode('utf-8'))
            supported_encodings = json.loads(info.properties.get(b'supported_encodings', b'[]').decode('utf-8'))
            
            # Construct EdgeNodeCapabilities object
            capabilities = EdgeNodeCapabilities(
                node_type=node_type,
                hardware_info=hardware_info,
                sensors=[SensorInfo(**sensor) for sensor in sensors],
                supported_encodings=supported_encodings
            )
            
            devices[device_id] = {
                "address": f"tcp://{address}:{port}",
                "capabilities": capabilities
            }
            logger.info(f"New device added: {device_id}")
    elif state_change is ServiceStateChange.Removed:
        # Remove the device if it's no longer available
        for device_id, device_info in list(devices.items()):
            if device_info["address"].split(":")[1].strip("//") == socket.inet_ntoa(info.addresses[0]):
                del devices[device_id]
                logger.info(f"Device removed: {device_id}")
                break
        else:
            logger.warning(f"No matching device found for removed service: {name}")
    else:
        logger.warning(f"Unhandled service state change: {state_change} for service: {name}")

# Initialize Zeroconf for service discovery
zeroconf = Zeroconf()
browser = ServiceBrowser(zeroconf, "_ministream._tcp.local.", handlers=[on_service_state_change])

class ConfigureStreamRequest(BaseModel):
    device_id: str
    config: StreamConfig

async def send_zmq_request(address: str, message: Dict) -> Dict:
    """
    Send a ZMQ request to a device and await the response.
    
    Args:
        address (str): The ZMQ address of the device.
        message (Dict): The message to send.
    
    Returns:
        Dict: The response from the device.
    
    Raises:
        CommunicationError: If there's an error communicating with the device.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(address)
    
    try:
        socket.send_json(message)
        response = await asyncio.wait_for(socket.recv_json(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.error(f"Timeout while communicating with device at {address}")
        raise CommunicationError(f"Timeout while communicating with device at {address}")
    except zmq.ZMQError as e:
        logger.error(f"ZMQ error while communicating with device at {address}: {str(e)}")
        raise CommunicationError(f"Error communicating with device at {address}: {str(e)}")
    finally:
        socket.close()
        context.term()
    
    return response

@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Welcome to the Ministream Network API"}

@app.get("/devices", response_model=List[str])
async def get_devices():
    """Get a list of all discovered device IDs."""
    logger.debug(f"Devices in get_devices(): {list(devices.keys())}")
    return list(devices.keys())

@app.get("/devices/{device_id}/status", response_model=DeviceStatus)
async def get_device_status(device_id: str):
    """
    Get the status of a specific device.
    
    Args:
        device_id (str): The ID of the device.
    
    Returns:
        DeviceStatus: The status of the device.
    
    Raises:
        HTTPException: If the device is not found or there's an error communicating with it.
    """
    try:
        if device_id not in devices:
            raise DeviceNotFoundError(f"Device not found: {device_id}")
        
        address = devices[device_id]["address"]
        response = await send_zmq_request(address, {"type": "get_status"})
        
        return DeviceStatus(**response)
    except DeviceNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except CommunicationError as e:
        logger.error(f"Communication error with device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.post("/devices/{device_id}/configure")
async def configure_stream(device_id: str, config: StreamConfig):
    """
    Configure the stream for a specific device.
    
    Args:
        device_id (str): The ID of the device.
        config (StreamConfig): The stream configuration.
    
    Returns:
        Dict: A status message indicating success or failure.
    
    Raises:
        HTTPException: If the device is not found or there's an error configuring the stream.
    """
    try:
        if device_id not in devices:
            raise DeviceNotFoundError(f"Device not found: {device_id}")
        
        address = devices[device_id]["address"]
        response = await send_zmq_request(address, {
            "type": "configure_stream",
            "config": config.dict()
        })
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        return {"status": "success", "message": "Stream configured successfully"}
    except DeviceNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except CommunicationError as e:
        logger.error(f"Communication error with device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.get("/devices/{device_id}/capabilities", response_model=EdgeNodeCapabilities)
async def get_device_capabilities(device_id: str):
    """
    Get the capabilities of a specific device.
    
    Args:
        device_id (str): The ID of the device.
    
    Returns:
        EdgeNodeCapabilities: The capabilities of the device.
    
    Raises:
        HTTPException: If the device is not found.
    """
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]["capabilities"]

@app.post("/devices/{device_id}/heartbeat")
async def device_heartbeat(device_id: str):
    if device_id in devices:
        devices[device_id]['last_heartbeat'] = time.time()
        devices[device_id]['status'] = 'online'
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=404, detail="Device not found")

# Add this route for testing CORS
@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS is working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
