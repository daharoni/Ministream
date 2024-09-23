from pydantic import BaseModel
from typing import List

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
