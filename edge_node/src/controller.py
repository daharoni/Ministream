import zmq
import zmq.asyncio
from shared.models import StreamConfig, DeviceStatus
from shared.exceptions import ConfigurationError, StreamError
from shared.logger import edge_node_logger as logger

class Controller:
    """
    The Controller class manages the communication and control of the edge node.
    It handles incoming messages, manages the sensor and streaming components,
    and provides status information about the device.
    """

    def __init__(self, sensor_manager, streamer, config):
        """
        Initialize the Controller with necessary components and configuration.

        Args:
            sensor_manager: The SensorManager instance for managing sensors.
            streamer: The Streamer instance for managing video streams.
            config (dict): Configuration dictionary for the Controller.
        """
        self.sensor_manager = sensor_manager
        self.streamer = streamer
        self.config = config
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.config.get('port', 5555)}")
        logger.info(f"Controller initialized on port {self.config.get('port', 5555)}")

    async def run(self):
        """
        The main loop of the Controller. It continuously listens for incoming
        messages, processes them, and sends responses.
        """
        logger.info("Controller starting")
        while True:
            message = await self.socket.recv_json()
            logger.debug(f"Received message: {message}")
            response = await self.handle_message(message)
            await self.socket.send_json(response)
            logger.debug(f"Sent response: {response}")

    async def handle_message(self, message):
        """
        Process incoming messages based on their type.

        Args:
            message (dict): The incoming message to process.

        Returns:
            dict: The response to the message.
        """
        if message['type'] == 'get_status':
            return self.get_status()
        elif message['type'] == 'configure_stream':
            return await self.configure_stream(message['config'])
        else:
            logger.warning(f"Unknown message type: {message['type']}")
            return {'error': 'Unknown message type'}

    def get_status(self):
        """
        Retrieve the current status of the device, including sensor information.

        Returns:
            dict: The device status.
        """
        sensors = self.sensor_manager.get_sensors()
        status = DeviceStatus(
            id="jetson_edge_node_0",
            status="running",
            sensors=sensors,
            online=True
        ).dict()
        logger.info(f"Device status: {status}")
        return status

    async def configure_stream(self, config):
        """
        Configure the video stream with the provided configuration.

        Args:
            config (dict): The stream configuration parameters.

        Returns:
            dict: A status message indicating success or failure.

        Raises:
            ConfigurationError: If the stream configuration is invalid.
            StreamError: If there's an error while configuring the stream.
        """
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
