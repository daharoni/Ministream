import React, { useState, useEffect } from 'react';
import { fetchDevices, fetchDeviceDetails } from './services/api';
import DeviceList from './components/DeviceList';
import DeviceDetails from './components/DeviceDetails';

function App() {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);

  useEffect(() => {
    fetchDevices()
      .then(fetchedDevices => {
        console.log('Fetched devices:', fetchedDevices);
        setDevices(fetchedDevices);
      })
      .catch(error => console.error('Error fetching devices:', error));
  }, []);

  const handleDeviceSelect = async (deviceId) => {
    console.log('Selected device ID:', deviceId);  // Add this line for debugging
    try {
      const deviceDetails = await fetchDeviceDetails(deviceId);
      console.log('Fetched device details:', deviceDetails);  // Add this line for debugging
      setSelectedDevice(deviceDetails);
    } catch (error) {
      console.error('Error fetching device details:', error);
      setSelectedDevice({ id: deviceId, error: 'Failed to fetch device details' });
    }
  };

  return (
    <div className="App">
      <h1>Ministream Control Panel</h1>
      <DeviceList devices={devices} onSelectDevice={handleDeviceSelect} />
      {selectedDevice && <DeviceDetails device={selectedDevice} />}
    </div>
  );
}

export default App;
