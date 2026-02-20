const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

// Health check
export const checkHealth = async () => {
  const response = await fetch(`${API_URL}/api/health`);
  return response.json();
};

// Auth
export const login = async (username, password) => {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return response.json();
};

// Students
export const getStudents = async () => {
  const response = await fetch(`${API_URL}/api/students`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const searchStudents = async (query) => {
  const response = await fetch(`${API_URL}/api/students/search?q=${encodeURIComponent(query)}`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const getStudent = async (indexNumber) => {
  const response = await fetch(`${API_URL}/api/students/${encodeURIComponent(indexNumber)}`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

// Results
export const getResults = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`${API_URL}/api/results?${params}`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const getPendingResults = async () => {
  const response = await fetch(`${API_URL}/api/results/pending`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const getResult = async (resultId) => {
  const response = await fetch(`${API_URL}/api/results/${resultId}`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

// Certificates
export const getCertificates = async () => {
  const response = await fetch(`${API_URL}/api/certificates`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const getCertificate = async (certificateId) => {
  const response = await fetch(`${API_URL}/api/certificates/${certificateId}`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const issueCertificate = async (resultId) => {
  const response = await fetch(`${API_URL}/api/certificates/issue`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ result_id: resultId })
  });
  return response.json();
};

export const getCertificateDownloadUrl = (certificateId) => {
  const token = localStorage.getItem('token');
  return `${API_URL}/api/certificates/${certificateId}/download?token=${token}`;
};

export const getCertificatePreviewUrl = (certificateId) => {
  const token = localStorage.getItem('token');
  return `${API_URL}/api/certificates/${certificateId}/preview?token=${token}`;
};

// Public verification - by verification code
// First tries blockchain, then falls back to database
export const verifyCertificate = async (data) => {
  // Try blockchain first
  try {
    const blockchainResponse = await fetch(`${API_URL}/api/certificate/verify-by-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const blockchainData = await blockchainResponse.json();
    
    if (blockchainData.verified || blockchainData.exists) {
      return {
        valid: blockchainData.verified,
        verified: blockchainData.verified,
        message: blockchainData.message,
        certificate: blockchainData.certificate_details,
        source: 'blockchain'
      };
    }
  } catch (e) {
    console.log('Blockchain verification failed, trying database...');
  }
  
  // Fall back to database
  const response = await fetch(`${API_URL}/api/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const dbData = await response.json();
  return { ...dbData, source: 'database' };
};

// Public verification - by student index number (blockchain)
export const verifyByIndexNumber = async (studentIndex) => {
  const response = await fetch(`${API_URL}/api/certificate/verify-by-index`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ student_index: studentIndex })
  });
  return response.json();
};

// Public verification - by uploading certificate file (blockchain)
export const verifyByFile = async (file) => {
  const formData = new FormData();
  formData.append('certificate', file);
  
  const response = await fetch(`${API_URL}/api/certificate/verify`, {
    method: 'POST',
    body: formData
  });
  return response.json();
};

// Dashboard stats
export const getDashboardStats = async () => {
  const response = await fetch(`${API_URL}/api/stats/dashboard`, {
    headers: getAuthHeaders()
  });
  return response.json();
};
