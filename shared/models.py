from pydantic import BaseModel
from typing import List, Dict

class SensorInfo(BaseModel):
    id: str
    name: str
    resolutions: List[str]
    max_fps: float

class StreamConfig(BaseModel):
    resolution: str
    fps: float
    encoding: str

class DeviceStatus(BaseModel):
    id: str
    status: str
    sensors: List[SensorInfo]

class EdgeNodeCapabilities(BaseModel):
    node_type: str
    hardware_info: Dict[str, str]
    sensors: List[SensorInfo]
    supported_encodings: List[str]

class EdgeNodeInfo(BaseModel):
    id: str
    ip_address: str
    port: int
    capabilities: EdgeNodeCapabilities
