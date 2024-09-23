import zmq
import zmq.asyncio
from models import StreamConfig, DeviceStatus

class Controller:
    def __init__(self, sensor_manager, streamer, config):
        self.sensor_manager = sensor_manager
        self.streamer = streamer
        self.config = config
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.config['port']}")

    async def run(self):
        while True:
            message = await self.socket.recv_json()
            response = await self.handle_message(message)
            await self.socket.send_json(response)

    async def handle_message(self, message):
        if message['type'] == 'get_status':
            return self.get_status()
        elif message['type'] == 'configure_stream':
            return await self.configure_stream(message['config'])
        else:
            return {'error': 'Unknown message type'}

    def get_status(self):
        sensors = self.sensor_manager.get_sensors()
        return DeviceStatus(
            id="jetson_edge_node_0",
            status="running",
            sensors=sensors
        ).dict()

    async def configure_stream(self, config):
        stream_config = StreamConfig(**config)
        # Update streamer configuration
        self.streamer.config.update(stream_config.dict())
        # Restart the stream with new configuration
        await self.streamer.stop()
        await self.streamer.run()
        return {'status': 'success'}
