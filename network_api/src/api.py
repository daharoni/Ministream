from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import zmq
import asyncio
import json

from shared.models import SensorInfo, StreamConfig, DeviceStatus, EdgeNodeCapabilities

app = FastAPI()

from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
import socket

devices = {}

def on_service_state_change(zeroconf, service_type, name, state_change):
    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        if info:
            address = socket.inet_ntoa(info.addresses[0])
            port = info.port
            device_id = info.properties.get(b'device_id', b'').decode('utf-8')
            capabilities = json.loads(info.properties.get(b'capabilities', b'{}').decode('utf-8'))
            devices[device_id] = {
                "address": f"tcp://{address}:{port}",
                "capabilities": EdgeNodeCapabilities(**capabilities)
            }

zeroconf = Zeroconf()
browser = ServiceBrowser(zeroconf, "_ministream._tcp.local.", handlers=[on_service_state_change])

class ConfigureStreamRequest(BaseModel):
    device_id: str
    config: StreamConfig

async def send_zmq_request(address: str, message: Dict) -> Dict:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(address)
    
    socket.send_json(message)
    response = socket.recv_json()
    
    socket.close()
    context.term()
    
    return response

@app.get("/")
async def root():
    return {"message": "Welcome to the Ministream Network API"}

@app.get("/devices", response_model=List[str])
async def get_devices():
    return list(devices.keys())

@app.get("/devices/{device_id}/status", response_model=DeviceStatus)
async def get_device_status(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    address = devices[device_id]["address"]
    response = await send_zmq_request(address, {"type": "get_status"})
    
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    
    return DeviceStatus(**response)

@app.post("/devices/{device_id}/configure")
async def configure_stream(device_id: str, config: StreamConfig):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    address = devices[device_id]["address"]
    response = await send_zmq_request(address, {
        "type": "configure_stream",
        "config": config.dict()
    })
    
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    
    return {"status": "success", "message": "Stream configured successfully"}

@app.get("/devices/{device_id}/capabilities", response_model=EdgeNodeCapabilities)
async def get_device_capabilities(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]["capabilities"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
