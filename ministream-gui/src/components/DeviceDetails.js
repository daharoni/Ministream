import React from 'react';

function DeviceDetails({ device }) {
  console.log('Device in DeviceDetails:', device);  // Add this line for debugging

  const renderValue = (value) => {
    if (typeof value === 'object' && value !== null) {
      return (
        <ul>
          {Object.entries(value).map(([subKey, subValue]) => (
            <li key={subKey}>
              <strong>{subKey}:</strong> {renderValue(subValue)}
            </li>
          ))}
        </ul>
      );
    }
    return JSON.stringify(value);
  };

  return (
    <div>
      <h2>Device Details</h2>
      {device ? (
        <ul>
          {Object.entries(device).map(([key, value]) => (
            <li key={key}>
              <strong>{key}:</strong> {renderValue(value)}
            </li>
          ))}
        </ul>
      ) : (
        <p>No device details available</p>
      )}
    </div>
  );
}

export default DeviceDetails;
