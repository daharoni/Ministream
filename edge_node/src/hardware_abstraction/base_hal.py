from abc import ABC, abstractmethod
from typing import List, Dict
from shared.models import StreamConfig

class BaseHAL(ABC):
    @abstractmethod
    def detect_sensors(self) -> List[Dict]:
        """
        Detect and return a list of available sensors.
        
        Returns:
            List[Dict]: A list of dictionaries containing sensor information.
        """
        pass

    @abstractmethod
    def start_stream(self, config: StreamConfig) -> None:
        """
        Start the video stream with the given configuration.
        
        Args:
            config (StreamConfig): The stream configuration.
        """
        pass

    @abstractmethod
    def get_frame(self):
        """
        Capture and return a single frame from the video stream.
        
        Returns:
            The captured frame (format may vary depending on the implementation).
        """
        pass

    @abstractmethod
    def stop_stream(self) -> None:
        """
        Stop the current video stream.
        """
        pass

    @abstractmethod
    def adjust_settings(self, settings: Dict) -> None:
        """
        Adjust camera settings.
        
        Args:
            settings (Dict): A dictionary of settings to adjust.
        """
        pass
