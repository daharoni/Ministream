import React from 'react';
import './DeviceDetails.css';

function DeviceDetails({ device }) {
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
    <div className="DeviceDetails">
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
        <p>No device selected</p>
      )}
    </div>
  );
}

export default DeviceDetails;
