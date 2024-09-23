import zmq
import json
from typing import Dict, Any

def send_zmq_request(address: str, message: Dict[str, Any]) -> Dict[str, Any]:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(address)
    
    socket.send_json(message)
    response = socket.recv_json()
    
    socket.close()
    context.term()
    
    return response

def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return json.load(f)
