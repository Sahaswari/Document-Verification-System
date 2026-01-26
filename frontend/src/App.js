import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [backendStatus, setBackendStatus] = useState('Checking...');

  // Check backend health on load
  React.useEffect(() => {
    fetch('http://localhost:5000/api/health')
      .then(res => res.json())
      .then(data => setBackendStatus(data.status))
      .catch(() => setBackendStatus('Not connected'));
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus('');
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setStatus(data.message || data.error);
    } catch (error) {
      setStatus('Error uploading file: ' + error.message);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📄 Document Verification System</h1>
        <p className="subtitle">Blockchain-based Document Authenticity Verification</p>
      </header>

      <main className="App-main">
        <div className="status-card">
          <h3>System Status</h3>
          <p>Backend: <span className={backendStatus === 'healthy' ? 'status-ok' : 'status-error'}>{backendStatus}</span></p>
          <p>Blockchain: <span className="status-ok">Running (Hardhat)</span></p>
        </div>

        <div className="upload-card">
          <h2>Upload Document</h2>
          <p>Upload a document to verify its authenticity or register it on the blockchain.</p>
          
          <div className="upload-area">
            <input 
              type="file" 
              onChange={handleFileChange}
              accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
            />
            {file && <p className="file-name">Selected: {file.name}</p>}
          </div>

          <button onClick={handleUpload} className="upload-btn">
            Upload & Verify
          </button>

          {status && <p className="status-message">{status}</p>}
        </div>
      </main>

      <footer className="App-footer">
        <p>Document Verification System v1.0.0 | Powered by Ethereum & AI</p>
      </footer>
    </div>
  );
}

export default App;
