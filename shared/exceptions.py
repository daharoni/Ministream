class MiniStreamException(Exception):
    """Base exception class for MiniStream project"""

class DeviceNotFoundError(MiniStreamException):
    """Raised when a requested device is not found"""

class CommunicationError(MiniStreamException):
    """Raised when there's an error in communication with a device"""

class ConfigurationError(MiniStreamException):
    """Raised when there's an error in configuration"""

class StreamError(MiniStreamException):
    """Raised when there's an error related to video streaming"""

class SensorError(MiniStreamException):
    """Raised when there's an error related to sensors"""

class AuthenticationError(MiniStreamException):
    """Raised when there's an authentication error"""

class AuthorizationError(MiniStreamException):
    """Raised when there's an authorization error"""

class ValidationError(MiniStreamException):
    """Raised when there's a validation error"""

class HardwareError(MiniStreamException):
    """Raised when there's a hardware-related error"""

class NetworkError(MiniStreamException):
    """Raised when there's a network-related error"""

class DatabaseError(MiniStreamException):
    """Raised when there's a database-related error"""

class APIError(MiniStreamException):
    """Raised when there's an API-related error"""

class GUIError(MiniStreamException):
    """Raised when there's a GUI-related error"""
