import React, { useState, useEffect } from 'react';
import { fetchDevices, fetchDeviceDetails, fetchDeviceStatus } from './services/api';
import DeviceList from './components/DeviceList';
import DeviceDetails from './components/DeviceDetails';
import './App.css'; // We'll create this file for custom styles

function App() {
  const [devices, setDevices] = useState([]);
  const [deviceStatuses, setDeviceStatuses] = useState({});
  const [selectedDevice, setSelectedDevice] = useState(null);

  useEffect(() => {
    const fetchDevicesAndStatuses = async () => {
      try {
        const fetchedDevices = await fetchDevices();
        console.log('Fetched devices in App:', fetchedDevices);
        setDevices(fetchedDevices);

        const statuses = {};
        for (const deviceId of fetchedDevices) {
          try {
            const status = await fetchDeviceStatus(deviceId);
            statuses[deviceId] = status;
          } catch (error) {
            console.error(`Error fetching status for device ${deviceId}:`, error);
            statuses[deviceId] = { error: 'Failed to fetch status', online: false };
          }
        }
        setDeviceStatuses(statuses);
      } catch (error) {
        console.error('Error fetching devices:', error);
        setDevices([]);
        setDeviceStatuses({});
      }
    };

    fetchDevicesAndStatuses();
    const interval = setInterval(fetchDevicesAndStatuses, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleDeviceSelect = async (deviceId) => {
    console.log('Selected device ID:', deviceId);
    try {
      const deviceDetails = await fetchDeviceDetails(deviceId);
      console.log('Fetched device details:', deviceDetails);
      setSelectedDevice({ id: deviceId, ...deviceDetails });
    } catch (error) {
      console.error('Error fetching device details:', error);
      setSelectedDevice({ id: deviceId, error: 'Failed to fetch device details' });
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Ministream Control Panel</h1>
      </header>
      <main className="App-main">
        <section className="App-device-list">
          <DeviceList 
            devices={devices} 
            deviceStatuses={deviceStatuses} 
            onSelectDevice={handleDeviceSelect} 
          />
        </section>
        <section className="App-device-details">
          {selectedDevice && <DeviceDetails device={selectedDevice} />}
        </section>
      </main>
    </div>
  );
}

export default App;
