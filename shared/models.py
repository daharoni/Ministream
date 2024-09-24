from pydantic import BaseModel
from typing import List, Dict, Optional

class SensorInfo(BaseModel):
    id: str
    name: str
    resolutions: List[str]
    max_fps: float

class StreamConfig(BaseModel):
    resolution: str
    fps: float
    encoding: str

class EdgeNodeCapabilities(BaseModel):
    node_type: str
    hardware_info: Dict[str, str]
    sensors: List[SensorInfo]
    supported_encodings: List[str]

class DeviceStatus(BaseModel):
    id: str
    status: Optional[str] = "running"
    sensors: List[str] = []
    online: bool = True

class Device(BaseModel):
    id: str
    ip_address: str
    port: int
    capabilities: EdgeNodeCapabilities
    status: DeviceStatus
    last_heartbeat: Optional[float] = None

class EdgeNodeInfo(BaseModel):
    id: str
    ip_address: str
    port: int
    capabilities: EdgeNodeCapabilities
