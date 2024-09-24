from fastapi import FastAPI, HTTPException
from typing import List, Dict
import zmq
import asyncio
import json
from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
import socket
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import time
from pydantic import BaseModel

from shared.models import Device, EdgeNodeCapabilities, SensorInfo, StreamConfig, DeviceStatus
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

devices: Dict[str, Device] = {}

HEARTBEAT_TIMEOUT = 10  # Timeout in seconds1

async def periodic_device_check():
    while True:
        current_time = time.time()
        for device_id, device in list(devices.items()):
            if current_time - device.last_heartbeat > HEARTBEAT_TIMEOUT:
                logger.warning(f"Device {device_id} missed heartbeat")
                device.status.status = 'offline'
                device.status.online = False
            else:
                device.status.status = 'running'
                device.status.online = True
        await asyncio.sleep(10)  # Check every 10 seconds

def on_service_state_change(zeroconf, service_type, name, state_change):
    logger.info(f"Service {name} of type {service_type} changed state to {state_change}")
    info = zeroconf.get_service_info(service_type, name)
    if not info:
        logger.warning(f"Failed to get service info for {name} of type {service_type}. State change: {state_change}")
        return

    if state_change is ServiceStateChange.Added:
        address = socket.inet_ntoa(info.addresses[0])
        port = info.port
        device_id = info.properties.get(b'device_id', b'').decode('utf-8')
        
        node_type = info.properties.get(b'node_type', b'').decode('utf-8')
        hardware_info = json.loads(info.properties.get(b'hardware_info', b'{}').decode('utf-8'))
        sensors = json.loads(info.properties.get(b'sensors', b'[]').decode('utf-8'))
        supported_encodings = json.loads(info.properties.get(b'supported_encodings', b'[]').decode('utf-8'))
        
        capabilities = EdgeNodeCapabilities(
            node_type=node_type,
            hardware_info=hardware_info,
            sensors=[SensorInfo(**sensor) for sensor in sensors],
            supported_encodings=supported_encodings
        )
        
        status = DeviceStatus(
            id=device_id,
            status="running",
            sensors=[sensor.id for sensor in capabilities.sensors],
            online=True
        )
        
        devices[device_id] = Device(
            id=device_id,
            ip_address=address,
            port=port,
            capabilities=capabilities,
            status=status,
            last_heartbeat=time.time()
        )
        logger.info(f"New device added: {device_id}")
    elif state_change is ServiceStateChange.Removed:
        for device_id, device in list(devices.items()):
            if device.ip_address == socket.inet_ntoa(info.addresses[0]):
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

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

async def send_zmq_request(address: str, message: Dict) -> Dict:
    def zmq_send_receive(address, message):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(address)
        try:
            socket.send_json(message)
            return socket.recv_json()
        finally:
            socket.close()
            context.term()

    try:
        return await asyncio.get_event_loop().run_in_executor(
            executor, zmq_send_receive, address, message
        )
    except Exception as e:
        logger.error(f"Error in send_zmq_request: {str(e)}", exc_info=True)
        raise CommunicationError(f"Error communicating with device at {address}: {str(e)}")

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
    try:
        if device_id not in devices:
            raise DeviceNotFoundError(f"Device not found: {device_id}")
        
        device = devices[device_id]
        
        # Check if the device is already marked as offline
        if not device.status.online:
            return device.status
        
        try:
            address = f"tcp://{device.ip_address}:{device.port}"
            response = await send_zmq_request(address, {"type": "get_status"})
            
            device.status.status = response.get('status', device.status.status)
            device.status.sensors = response.get('sensors', device.status.sensors)
            device.status.online = True
        except CommunicationError:
            # If communication fails, mark the device as offline
            device.status.online = False
            device.status.status = "Offline"
        
        return device.status
    except DeviceNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_device_status: {str(e)}", exc_info=True)
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
        
        device = devices[device_id]
        address = f"tcp://{device.ip_address}:{device.port}"
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
    return devices[device_id].capabilities

@app.post("/devices/{device_id}/heartbeat")
async def device_heartbeat(device_id: str):
    if device_id in devices:
        devices[device_id].last_heartbeat = time.time()
        devices[device_id].status.status = 'running'
        devices[device_id].status.online = True
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
