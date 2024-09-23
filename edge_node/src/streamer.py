import asyncio
import cv2
import zmq
import zmq.asyncio

class Streamer:
    def __init__(self, hal, config):
        self.hal = hal
        self.config = config
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{self.config['port']}")

    async def run(self):
        self.hal.start_stream(self.config)
        while True:
            frame = self.hal.get_frame()
            _, encoded_frame = cv2.imencode('.jpg', frame)
            await self.socket.send(encoded_frame.tobytes())
            await asyncio.sleep(1 / self.config['fps'])

    async def stop(self):
        self.hal.stop_stream()
        self.socket.close()
