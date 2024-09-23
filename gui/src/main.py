import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QComboBox, QLineEdit, QMessageBox, QTabWidget
from PyQt6.QtCore import Qt
import requests
import json

class MinistreamGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ministream Control Panel")
        self.setGeometry(100, 100, 800, 600)
        self.api_url = "http://localhost:8000"  # Adjust this if your network_api is running elsewhere

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.setup_devices_tab()
        self.setup_stream_tab()

    def setup_devices_tab(self):
        devices_tab = QWidget()
        devices_layout = QVBoxLayout(devices_tab)

        self.devices_list = QListWidget()
        devices_layout.addWidget(self.devices_list)

        button_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh Devices")
        refresh_button.clicked.connect(self.refresh_devices)
        button_layout.addWidget(refresh_button)

        details_button = QPushButton("Show Device Details")
        details_button.clicked.connect(self.show_device_details)
        button_layout.addWidget(details_button)

        devices_layout.addLayout(button_layout)
        self.tab_widget.addTab(devices_tab, "Devices")

    def setup_stream_tab(self):
        stream_tab = QWidget()
        stream_layout = QVBoxLayout(stream_tab)

        stream_layout.addWidget(QLabel("Select Device:"))
        self.device_dropdown = QComboBox()
        stream_layout.addWidget(self.device_dropdown)

        stream_layout.addWidget(QLabel("Resolution:"))
        self.resolution_dropdown = QComboBox()
        stream_layout.addWidget(self.resolution_dropdown)

        stream_layout.addWidget(QLabel("FPS:"))
        self.fps_entry = QLineEdit()
        stream_layout.addWidget(self.fps_entry)

        stream_layout.addWidget(QLabel("Encoding:"))
        self.encoding_dropdown = QComboBox()
        stream_layout.addWidget(self.encoding_dropdown)

        configure_button = QPushButton("Configure Stream")
        configure_button.clicked.connect(self.configure_stream)
        stream_layout.addWidget(configure_button)

        stream_layout.addStretch(1)
        self.tab_widget.addTab(stream_tab, "Stream Control")

    def refresh_devices(self):
        try:
            response = requests.get(f"{self.api_url}/devices")
            devices = response.json()
            self.devices_list.clear()
            self.device_dropdown.clear()
            for device in devices:
                self.devices_list.addItem(device)
                self.device_dropdown.addItem(device)
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch devices: {str(e)}")

    def show_device_details(self):
        selected_items = self.devices_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Info", "Please select a device first.")
            return
        device_id = selected_items[0].text()
        try:
            response = requests.get(f"{self.api_url}/devices/{device_id}/capabilities")
            capabilities = response.json()
            details = json.dumps(capabilities, indent=2)
            QMessageBox.information(self, "Device Details", details)

            # Update stream control options based on capabilities
            self.resolution_dropdown.clear()
            self.resolution_dropdown.addItems(capabilities['sensors'][0]['resolutions'])
            self.encoding_dropdown.clear()
            self.encoding_dropdown.addItems(capabilities['supported_encodings'])
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch device details: {str(e)}")

    def configure_stream(self):
        device_id = self.device_dropdown.currentText()
        if not device_id:
            QMessageBox.information(self, "Info", "Please select a device first.")
            return
        config = {
            "resolution": self.resolution_dropdown.currentText(),
            "fps": float(self.fps_entry.text()),
            "encoding": self.encoding_dropdown.currentText()
        }
        try:
            response = requests.post(f"{self.api_url}/devices/{device_id}/configure", json=config)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Stream configured successfully.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to configure stream: {response.text}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to configure stream: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinistreamGUI()
    window.show()
    sys.exit(app.exec())
