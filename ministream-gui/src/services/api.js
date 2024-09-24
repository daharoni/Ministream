const API_BASE_URL = 'http://localhost:8000'; // Adjust if necessary

export const fetchDevices = async () => {
  try {
    console.log('Fetching devices...');
    const response = await fetch(`${API_BASE_URL}/devices`);
    console.log('Response status:', response.status);
    if (!response.ok) {
      throw new Error('Failed to fetch devices');
    }
    const data = await response.json();
    console.log('Raw API response:', data);
    return data;
  } catch (error) {
    console.error('Error in fetchDevices:', error);
    throw error;
  }
};

export const fetchDeviceDetails = async (deviceId) => {
  try {
    console.log('Fetching device details for:', deviceId);
    const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/capabilities`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('Device details:', data);
    return data;
  } catch (error) {
    console.error('Error in fetchDeviceDetails:', error);
    throw error;
  }
};

// Add this new function
export const fetchDeviceStatus = async (deviceId) => {
  try {
    console.log('Fetching status for device:', deviceId);
    const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/status`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('Device status:', data);
    return data;
  } catch (error) {
    console.error('Error in fetchDeviceStatus:', error);
    throw error;
  }
};
