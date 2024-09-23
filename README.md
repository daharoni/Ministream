# Ministream

Ministream is a flexible, networked image streaming system capable of running on various edge computing devices such as NVIDIA Jetson Orin Nanos, Raspberry Pis, Zynq SoCs, and MCUs. The system allows users to discover, configure, and stream video data from multiple devices over a local network.

## Project Structure

The project is organized as a monorepo with the following main components:

- `edge_node/`: Software running on edge devices for image acquisition, configuration, and streaming.
- `network_api/`: API for device discovery and management.
- `gui/`: Client application for interacting with edge devices.
- `shared/`: Shared models and utilities used across components.
- `docs/`: Project documentation.
- `scripts/`: Utility scripts for deployment and setup.
- `configs/`: Configuration files for different edge node setups.

## Features

- Automatic discovery of edge nodes on the network
- Retrieval of edge node capabilities (hardware info, sensors, supported encodings)
- Configuration and management of video streams
- Support for multiple edge node types (Jetson, Raspberry Pi, Zynq)

## Getting Started

### Prerequisites

- Python 3.8+
- Docker (for containerized components)
- GStreamer
- ZeroMQ

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/Ministream.git
   cd Ministream
   ```

2. Set up virtual environments for each component (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Configuration

Ministream uses YAML configuration files located in the `configs/` directory. You can specify which configuration file to use by setting the `MINISTREAM_CONFIG` environment variable.

### Running the Edge Node

To run the edge node with a specific configuration:

```bash
MINISTREAM_CONFIG=configs/jetson_orin/config_8k.yaml python edge_node/src/main.py
```

### Running the Network API

To run the network API:

```bash
python network_api/src/main.py
```

## API Endpoints

- `GET /devices`: List all discovered devices
- `GET /devices/{device_id}/status`: Get status of a specific device
- `GET /devices/{device_id}/capabilities`: Get capabilities of a specific device
- `POST /devices/{device_id}/configure`: Configure stream settings for a device

## Testing

To run all tests:

```bash
pytest
```

To run specific tests:

```bash
pytest tests/test_capabilities.py  # Run capabilities tests
pytest edge_node/tests/  # Run edge node specific tests
pytest network_api/tests/  # Run network API specific tests
```

## Documentation

For more detailed information about the project, its components, and how to use them, please refer to the `docs/` directory.

## Contributing

Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.
