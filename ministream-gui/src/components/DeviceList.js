import React from 'react';
import './DeviceList.css';

function DeviceList({ devices, onSelectDevice }) {
  return (
    <div className="DeviceList">
      <h2>Devices</h2>
      {devices.length === 0 ? (
        <p>No devices found.</p>
      ) : (
        <ul>
          {devices.map(device => (
            <li 
              key={device.id} 
              onClick={() => onSelectDevice(device.id)}
              className={device.status === 'offline' ? 'offline' : 'online'}
            >
              {device.id} - Status: {device.status}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default DeviceList;
