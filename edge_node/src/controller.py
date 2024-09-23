import zmq
import zmq.asyncio
from shared.models import StreamConfig, DeviceStatus
from shared.exceptions import ConfigurationError, StreamError
from shared.logger import edge_node_logger as logger

class Controller:
    def __init__(self, sensor_manager, streamer, config):
        self.sensor_manager = sensor_manager
        self.streamer = streamer
        self.config = config
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.config.get('port', 5555)}")
        logger.info(f"Controller initialized on port {self.config.get('port', 5555)}")

    async def run(self):
        logger.info("Controller starting")
        while True:
            message = await self.socket.recv_json()
            logger.debug(f"Received message: {message}")
            response = await self.handle_message(message)
            await self.socket.send_json(response)
            logger.debug(f"Sent response: {response}")

    async def handle_message(self, message):
        if message['type'] == 'get_status':
            return self.get_status()
        elif message['type'] == 'configure_stream':
            return await self.configure_stream(message['config'])
        else:
            logger.warning(f"Unknown message type: {message['type']}")
            return {'error': 'Unknown message type'}

    def get_status(self):
        sensors = self.sensor_manager.get_sensors()
        status = DeviceStatus(
            id="jetson_edge_node_0",
            status="running",
            sensors=sensors
        ).dict()
        logger.info(f"Device status: {status}")
        return status

    async def configure_stream(self, config):
        try:
            stream_config = StreamConfig(**config)
            logger.info(f"Configuring stream with: {stream_config}")
            # Update streamer configuration
            self.streamer.config.update(stream_config.dict())
            # Restart the stream with new configuration
            await self.streamer.stop()
            await self.streamer.run()
            logger.info("Stream reconfigured and restarted")
            return {'status': 'success'}
        except ValueError as e:
            logger.error(f"Invalid stream configuration: {str(e)}")
            raise ConfigurationError(f"Invalid stream configuration: {str(e)}")
        except Exception as e:
            logger.error(f"Error configuring stream: {str(e)}")
            raise StreamError(f"Error configuring stream: {str(e)}")
