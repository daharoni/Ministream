import React from 'react';
import './DeviceList.css';

function DeviceList({ devices, onSelectDevice }) {
  console.log('Devices in DeviceList:', devices);  // Keep this for debugging

  return (
    <div className="DeviceList">
      <h2>Devices</h2>
      {devices.length === 0 ? (
        <p>No devices found.</p>
      ) : (
        <ul>
          {devices.map(device => {
            console.log('Individual device:', device);  // Log each device
            return (
              <li key={device} onClick={() => onSelectDevice(device)}>
                {typeof device === 'string' ? device : JSON.stringify(device)}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default DeviceList;
