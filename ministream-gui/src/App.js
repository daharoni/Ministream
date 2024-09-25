import React, { useState, useEffect } from 'react';
import { fetchDevices, fetchDeviceStatus, fetchDeviceDetails } from './services/api';
import DeviceList from './components/DeviceList';
import DeviceDetails from './components/DeviceDetails';
import SystemTopology from './components/SystemTopology';
import './App.css'; // We'll create this file for custom styles

function App() {
  const [devices, setDevices] = useState([]);
  const [deviceStatuses, setDeviceStatuses] = useState({});
  const [selectedDevice, setSelectedDevice] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const fetchedDevices = await fetchDevices();
        setDevices(fetchedDevices);
        
        const statuses = {};
        for (const deviceId of fetchedDevices) {
          const status = await fetchDeviceStatus(deviceId);
          statuses[deviceId] = status;
        }
        setDeviceStatuses(statuses);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds

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
        <section className="system-topology-container">
          <SystemTopology />
        </section>
        <div className="device-info-container">
          <section className="device-list-container">
            <h2>Devices</h2>
            <DeviceList 
              devices={devices} 
              deviceStatuses={deviceStatuses} 
              onSelectDevice={handleDeviceSelect} 
            />
          </section>
          <section className="device-details-container">
            <h2>Device Details</h2>
            {selectedDevice && <DeviceDetails device={selectedDevice} />}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
