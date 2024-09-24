import React, { useState, useEffect } from 'react';
import { fetchDevices, fetchDeviceDetails } from './services/api';
import DeviceList from './components/DeviceList';
import DeviceDetails from './components/DeviceDetails';
import './App.css'; // We'll create this file for custom styles

function App() {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);

  useEffect(() => {
    const fetchDevicesInterval = setInterval(() => {
      fetchDevices()
        .then(fetchedDevices => {
          console.log('Fetched devices:', fetchedDevices);
          setDevices(fetchedDevices);
        })
        .catch(error => console.error('Error fetching devices:', error));
    }, 5000);  // Fetch devices every 5 seconds

    return () => clearInterval(fetchDevicesInterval);
  }, []);

  const handleDeviceSelect = async (deviceId) => {
    console.log('Selected device ID:', deviceId);
    try {
      const deviceDetails = await fetchDeviceDetails(deviceId);
      console.log('Fetched device details:', deviceDetails);
      setSelectedDevice(deviceDetails);
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
          <DeviceList devices={devices} onSelectDevice={handleDeviceSelect} />
        </section>
        <section className="App-device-details">
          {selectedDevice && <DeviceDetails device={selectedDevice} />}
        </section>
      </main>
    </div>
  );
}

export default App;
