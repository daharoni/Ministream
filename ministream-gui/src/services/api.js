const API_URL = 'http://localhost:8000'; // Make sure this matches your API server address

export async function fetchDevices() {
  const response = await fetch(`${API_URL}/devices`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function fetchDeviceDetails(deviceId) {
  const response = await fetch(`${API_URL}/devices/${deviceId}/capabilities`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function configureStream(deviceId, config) {
  const response = await fetch(`${API_URL}/devices/${deviceId}/configure`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(config),
  });
  return response.json();
}
