import React from 'react';
import './DeviceList.css';

function DeviceList({ devices = [], deviceStatuses = {}, onSelectDevice }) {
  console.log('Devices in DeviceList:', devices);
  console.log('Device Statuses:', deviceStatuses);

  return (
    <div className="DeviceList">
      {devices.length === 0 ? (
        <p>No devices found.</p>
      ) : (
        <ul>
          {devices.map(deviceId => (
            <li 
              key={deviceId}
              onClick={() => onSelectDevice(deviceId)}
              className={deviceStatuses[deviceId]?.online ? 'online' : 'offline'}
            >
              Device ID: {deviceId} | Status: {
                deviceStatuses[deviceId]?.error 
                  ? 'Error fetching status' 
                  : (deviceStatuses[deviceId]?.online ? 'Online' : 'Offline')
              }
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default DeviceList;
