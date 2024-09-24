import sys
import os
import pytest
import requests
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from gui.src.main import MinistreamGUI

@pytest.fixture(scope="session")
def qapp():
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def app(qtbot):
    """Fixture to create and initialize the application window."""
    test_app = MinistreamGUI(test_mode=True)
    qtbot.addWidget(test_app)
    return test_app

def test_initial_state(app):
    """Test to verify the initial state of the application."""
    assert app.windowTitle() == "Ministream Control Panel"
    assert app.devices_list.count() == 0

def test_refresh_devices(app, qtbot, mocker):
    """Test to check device list refresh behavior."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = ['device1', 'device2']
    mocker.patch('requests.get', return_value=mock_response)
    
    qtbot.mouseClick(app.refresh_button, Qt.MouseButton.LeftButton)
    
    assert app.devices_list.count() == 2
    assert app.devices_list.item(0).text() == 'device1'
    assert app.devices_list.item(1).text() == 'device2'

def test_show_device_details(app, qtbot, mocker):
    """Test to check if device details are displayed correctly."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        'id': 'device1',
        'status': 'running',
        'sensors': [{'id': 'sensor1', 'name': 'Camera 1', 'resolutions': ['1280x720', '1920x1080']}],
        'supported_encodings': ['h264', 'h265']
    }
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    app.devices_list.addItem('device1')
    app.devices_list.setCurrentRow(0)  # Select the first device

    # Simulate button click to show device details
    qtbot.mouseClick(app.details_button, Qt.MouseButton.LeftButton)

    # Verify the get request was called
    mock_get.assert_called_once_with(f"{app.api_url}/devices/device1/capabilities")

    # Verify the dropdowns were updated correctly
    assert app.resolution_dropdown.count() == 2
    assert app.resolution_dropdown.itemText(0) == '1280x720'
    assert app.resolution_dropdown.itemText(1) == '1920x1080'
    assert app.encoding_dropdown.count() == 2
    assert app.encoding_dropdown.itemText(0) == 'h264'
    assert app.encoding_dropdown.itemText(1) == 'h265'

def test_configure_stream(app, qtbot, mocker):
    """Test to check stream configuration."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_post = mocker.patch('requests.post', return_value=mock_response)
    
    app.device_dropdown.addItem('device1')
    app.device_dropdown.setCurrentIndex(0)
    app.resolution_dropdown.addItem('1280x720')
    app.resolution_dropdown.setCurrentIndex(0)
    app.fps_entry.setText('30')
    app.encoding_dropdown.addItem('h264')
    app.encoding_dropdown.setCurrentIndex(0)
    
    qtbot.mouseClick(app.configure_button, Qt.MouseButton.LeftButton)
    
    mock_post.assert_called_once_with(
        'http://localhost:8000/devices/device1/configure',
        json={'resolution': '1280x720', 'fps': 30.0, 'encoding': 'h264'}
    )

def test_error_handling(app, qtbot, mocker):
    """Test to check error handling when refreshing devices."""
    mocker.patch('requests.get', side_effect=Exception("Network error"))
    
    mock_critical = mocker.patch.object(QMessageBox, 'critical', return_value=QMessageBox.StandardButton.Ok)
    
    qtbot.mouseClick(app.refresh_button, Qt.MouseButton.LeftButton)
    
    mock_critical.assert_called_once_with(app, "Error", "Failed to fetch devices: Network error")

# Add more tests as needed
