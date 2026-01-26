import React, { useState, useRef } from 'react';
import { verifyCertificate, verifyByIndexNumber, verifyByFile } from '../services/api';
import './VerifyPage.css';

const VerifyPage = () => {
  const [activeMethod, setActiveMethod] = useState('code'); // 'code', 'index', 'file'
  const [verificationCode, setVerificationCode] = useState('');
  const [indexNumber, setIndexNumber] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const resetForm = () => {
    setResult(null);
    setError(null);
  };

  const handleMethodChange = (method) => {
    setActiveMethod(method);
    resetForm();
  };

  // Method 1: Verify by verification code
  const handleVerifyByCode = async (e) => {
    e.preventDefault();
    
    if (!verificationCode.trim()) {
      setError('Please enter a verification code');
      return;
    }

    setLoading(true);
    resetForm();

    try {
      const data = await verifyCertificate({ verification_code: verificationCode.trim() });
      
      if (data.valid) {
        setResult({ ...data, method: 'code' });
      } else {
        setError(data.message || 'Certificate not found or invalid');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }

    setLoading(false);
  };

  // Method 2: Verify by student index number (blockchain)
  const handleVerifyByIndex = async (e) => {
    e.preventDefault();
    
    if (!indexNumber.trim()) {
      setError('Please enter a student index number');
      return;
    }

    setLoading(true);
    resetForm();

    try {
      const data = await verifyByIndexNumber(indexNumber.trim());
      
      if (data.verified) {
        setResult({ 
          valid: true,
          method: 'blockchain',
          blockchain: data.details,
          message: 'Certificate verified on blockchain'
        });
      } else if (data.error) {
        setError(data.error);
      } else {
        setError(data.message || 'Certificate not found on blockchain');
      }
    } catch (err) {
      setError('Blockchain verification failed. Make sure the blockchain service is running.');
    }

    setLoading(false);
  };

  // Method 3: Verify by uploading file (blockchain)
  const handleVerifyByFile = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select a certificate file');
      return;
    }

    setLoading(true);
    resetForm();

    try {
      const data = await verifyByFile(selectedFile);
      
      if (data.verified) {
        setResult({ 
          valid: true,
          method: 'file',
          blockchain: data.certificate_details,
          message: data.message || 'Certificate verified successfully'
        });
      } else if (data.exists === false) {
        setError(data.warning || 'Certificate not found on blockchain. This certificate may not be registered or could be fraudulent.');
      } else {
        setError(data.message || data.error || 'Certificate verification failed');
      }
    } catch (err) {
      setError('File verification failed. Make sure the blockchain service is running.');
    }

    setLoading(false);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
      if (!validTypes.includes(file.type)) {
        setError('Please select a valid PDF or image file');
        return;
      }
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect({ target: { files: [file] } });
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const getGradeClass = (grade) => {
    switch (grade) {
      case 'A': return 'grade-a';
      case 'B': return 'grade-b';
      case 'C': return 'grade-c';
      case 'S': return 'grade-s';
      default: return 'grade-default';
    }
  };

  const renderVerificationForm = () => {
    switch (activeMethod) {
      case 'code':
        return (
          <form onSubmit={handleVerifyByCode}>
            <div className="input-group">
              <label htmlFor="code">Verification Code</label>
              <input
                type="text"
                id="code"
                placeholder="e.g., DOE-OL2023-XXXXXXXX"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.toUpperCase())}
                className={error ? 'input-error' : ''}
              />
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'Verifying...' : '✓ Verify Certificate'}
            </button>
          </form>
        );
      
      case 'index':
        return (
          <form onSubmit={handleVerifyByIndex}>
            <div className="input-group">
              <label htmlFor="indexNumber">Student Index Number</label>
              <input
                type="text"
                id="indexNumber"
                placeholder="e.g., 2023-OL-123456"
                value={indexNumber}
                onChange={(e) => setIndexNumber(e.target.value.toUpperCase())}
                className={error ? 'input-error' : ''}
              />
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'Searching Blockchain...' : '🔗 Verify on Blockchain'}
            </button>
          </form>
        );
      
      case 'file':
        return (
          <form onSubmit={handleVerifyByFile}>
            <div 
              className={`file-upload-area ${selectedFile ? 'has-file' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept=".pdf,.png,.jpg,.jpeg"
                style={{ display: 'none' }}
              />
              {selectedFile ? (
                <div className="selected-file">
                  <span className="file-icon">📄</span>
                  <span className="file-name">{selectedFile.name}</span>
                  <span className="file-size">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                  <button 
                    type="button" 
                    className="remove-file"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                    }}
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <div className="upload-prompt">
                  <span className="upload-icon">📤</span>
                  <p>Drag and drop your certificate here</p>
                  <p className="upload-hint">or click to browse</p>
                  <p className="file-types">Supports: PDF, PNG, JPG (max 10MB)</p>
                </div>
              )}
            </div>
            <button type="submit" disabled={loading || !selectedFile}>
              {loading ? 'Verifying File...' : '🔍 Verify Uploaded File'}
            </button>
          </form>
        );
      
      default:
        return null;
    }
  };

  const renderMethodInfo = () => {
    switch (activeMethod) {
      case 'code':
        return (
          <div className="info-card">
            <h3>ℹ️ How to find the verification code?</h3>
            <p>The verification code is located at the bottom of your certificate, below the QR code. It starts with "DOE-" followed by the exam type and a unique identifier.</p>
            <div className="example-code">
              Example: <code>DOE-OL2023-A1B2C3D4</code>
            </div>
          </div>
        );
      
      case 'index':
        return (
          <div className="info-card blockchain-info-card">
            <h3>🔗 Blockchain Verification</h3>
            <p>This method searches the blockchain directly using your student index number. The index number is printed on your certificate and exam results slip.</p>
            <div className="example-code">
              Example: <code>2023-OL-123456</code> or <code>2024-AL-789012</code>
            </div>
            <div className="blockchain-badge">
              <span>⛓️</span> Verified on Ethereum Blockchain
            </div>
          </div>
        );
      
      case 'file':
        return (
          <div className="info-card file-info-card">
            <h3>📁 File Hash Verification</h3>
            <p>Upload your certificate PDF or image. The system calculates a unique hash (digital fingerprint) of your file and checks if it matches the hash stored on the blockchain.</p>
            <div className="security-note">
              <span>🔒</span> Your file is processed securely and not stored on our servers.
            </div>
            <div className="blockchain-badge">
              <span>⛓️</span> Verified on Ethereum Blockchain
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  const renderDatabaseResult = () => (
    <section className="result-section">
      <div className="result-card valid">
        <div className="result-header">
          <div className="valid-badge">
            <span className="checkmark">✓</span>
            <span>VERIFIED</span>
          </div>
          <p>This certificate is authentic and registered in the system.</p>
        </div>

        <div className="certificate-details">
          <div className="detail-group">
            <h4>Student Information</h4>
            <div className="detail-row">
              <span className="label">Full Name (English)</span>
              <span className="value">{result.certificate.student.full_name}</span>
            </div>
            <div className="detail-row">
              <span className="label">Full Name (Sinhala)</span>
              <span className="value sinhala">{result.certificate.student.full_name_sinhala || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="label">Full Name (Tamil)</span>
              <span className="value tamil">{result.certificate.student.full_name_tamil || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="label">Date of Birth</span>
              <span className="value">{result.certificate.student.date_of_birth}</span>
            </div>
            <div className="detail-row">
              <span className="label">School</span>
              <span className="value">{result.certificate.student.school_name}</span>
            </div>
            <div className="detail-row">
              <span className="label">District</span>
              <span className="value">{result.certificate.student.district}</span>
            </div>
          </div>

          <div className="detail-group">
            <h4>Examination Details</h4>
            <div className="detail-row">
              <span className="label">Examination</span>
              <span className="value">
                <span className={`exam-badge ${result.certificate.result.exam_type === 'OL' ? 'ol' : 'al'}`}>
                  G.C.E. {result.certificate.result.exam_type === 'OL' ? 'Ordinary Level' : 'Advanced Level'}
                </span>
              </span>
            </div>
            <div className="detail-row">
              <span className="label">Year</span>
              <span className="value">{result.certificate.result.exam_year}</span>
            </div>
            <div className="detail-row">
              <span className="label">Index Number</span>
              <span className="value"><strong>{result.certificate.result.index_number}</strong></span>
            </div>
            {result.certificate.result.z_score && (
              <div className="detail-row">
                <span className="label">Z-Score</span>
                <span className="value z-score">{result.certificate.result.z_score}</span>
              </div>
            )}
            {result.certificate.result.district_rank && (
              <div className="detail-row">
                <span className="label">District Rank</span>
                <span className="value">{result.certificate.result.district_rank}</span>
              </div>
            )}
            {result.certificate.result.island_rank && (
              <div className="detail-row">
                <span className="label">Island Rank</span>
                <span className="value">{result.certificate.result.island_rank}</span>
              </div>
            )}
          </div>
        </div>

        {/* Subject Results Table */}
        <div className="subjects-section">
          <h4>📚 Subject Results</h4>
          <table className="subjects-table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Grade</th>
              </tr>
            </thead>
            <tbody>
              {result.certificate.result.subjects.map((subject, index) => (
                <tr key={index}>
                  <td>{subject.subject_name}</td>
                  <td>
                    <span className={`grade ${getGradeClass(subject.grade)}`}>
                      {subject.grade}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Certificate Info */}
        <div className="blockchain-section">
          <h4>🔐 Certificate Information</h4>
          <div className="blockchain-info">
            <div className="detail-row">
              <span className="label">Certificate ID</span>
              <span className="value"><code>{result.certificate.certificate_id}</code></span>
            </div>
            <div className="detail-row">
              <span className="label">Document Hash</span>
              <span className="value hash"><code>{result.certificate.document_hash}</code></span>
            </div>
            {result.certificate.blockchain_tx_hash && (
              <div className="detail-row">
                <span className="label">Blockchain TX</span>
                <span className="value hash"><code>{result.certificate.blockchain_tx_hash}</code></span>
              </div>
            )}
            <div className="detail-row">
              <span className="label">Issued On</span>
              <span className="value">{new Date(result.certificate.issued_at).toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );

  const renderBlockchainResult = () => (
    <section className="result-section">
      <div className="result-card valid blockchain-verified">
        <div className="result-header">
          <div className="valid-badge blockchain">
            <span className="checkmark">⛓️</span>
            <span>BLOCKCHAIN VERIFIED</span>
          </div>
          <p>{result.message}</p>
        </div>

        <div className="blockchain-details">
          <h4>🔗 Blockchain Record Details</h4>
          <div className="detail-grid">
            {result.blockchain.document_hash && (
              <div className="detail-row">
                <span className="label">Document Hash</span>
                <span className="value hash"><code>{result.blockchain.document_hash}</code></span>
              </div>
            )}
            {result.blockchain.student_index && (
              <div className="detail-row">
                <span className="label">Student Index</span>
                <span className="value"><strong>{result.blockchain.student_index}</strong></span>
              </div>
            )}
            {result.blockchain.document_type && (
              <div className="detail-row">
                <span className="label">Document Type</span>
                <span className="value">{result.blockchain.document_type}</span>
              </div>
            )}
            {result.blockchain.exam_year && (
              <div className="detail-row">
                <span className="label">Exam Year</span>
                <span className="value">{result.blockchain.exam_year}</span>
              </div>
            )}
            {result.blockchain.issuer && (
              <div className="detail-row">
                <span className="label">Issuer Address</span>
                <span className="value hash"><code>{result.blockchain.issuer}</code></span>
              </div>
            )}
            {result.blockchain.owner && (
              <div className="detail-row">
                <span className="label">Owner Address</span>
                <span className="value hash"><code>{result.blockchain.owner}</code></span>
              </div>
            )}
            {result.blockchain.timestamp && (
              <div className="detail-row">
                <span className="label">Registration Time</span>
                <span className="value">{new Date(result.blockchain.timestamp * 1000).toLocaleString()}</span>
              </div>
            )}
            {result.blockchain.registration_timestamp && (
              <div className="detail-row">
                <span className="label">Registration Time</span>
                <span className="value">{new Date(result.blockchain.registration_timestamp * 1000).toLocaleString()}</span>
              </div>
            )}
            {result.blockchain.is_valid !== undefined && (
              <div className="detail-row">
                <span className="label">Status</span>
                <span className={`value status ${result.blockchain.is_valid ? 'active' : 'revoked'}`}>
                  {result.blockchain.is_valid ? '✓ Active' : '✗ Revoked'}
                </span>
              </div>
            )}
            {result.blockchain.ipfs_hash && (
              <div className="detail-row">
                <span className="label">IPFS Hash</span>
                <span className="value hash"><code>{result.blockchain.ipfs_hash}</code></span>
              </div>
            )}
          </div>
        </div>

        <div className="verification-note">
          <span>✓</span> This certificate's authenticity has been verified against the Ethereum blockchain.
        </div>
      </div>
    </section>
  );

  return (
    <div className="verify-page">
      {/* Header */}
      <header className="verify-header">
        <div className="header-content">
          <div className="emblem">🇱🇰</div>
          <div className="header-text">
            <h1>Department of Examinations - Sri Lanka</h1>
            <p>G.C.E. Certificate Verification Portal</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="verify-main">
        <div className="verify-container">
          {/* Verification Method Tabs */}
          <section className="method-tabs-section">
            <h2>Choose Verification Method</h2>
            <div className="method-tabs">
              <button
                className={`method-tab ${activeMethod === 'code' ? 'active' : ''}`}
                onClick={() => handleMethodChange('code')}
              >
                <span className="tab-icon">🔑</span>
                <span className="tab-label">Verification Code</span>
                <span className="tab-desc">Enter code from certificate</span>
              </button>
              <button
                className={`method-tab ${activeMethod === 'index' ? 'active' : ''}`}
                onClick={() => handleMethodChange('index')}
              >
                <span className="tab-icon">🔗</span>
                <span className="tab-label">Index Number</span>
                <span className="tab-desc">Blockchain lookup</span>
              </button>
              <button
                className={`method-tab ${activeMethod === 'file' ? 'active' : ''}`}
                onClick={() => handleMethodChange('file')}
              >
                <span className="tab-icon">📄</span>
                <span className="tab-label">Upload File</span>
                <span className="tab-desc">Verify PDF/Image</span>
              </button>
            </div>
          </section>

          {/* Verification Form */}
          <section className="verify-form-section">
            <div className="form-card">
              <h2>
                {activeMethod === 'code' && '🔍 Verify by Code'}
                {activeMethod === 'index' && '🔗 Verify by Index Number'}
                {activeMethod === 'file' && '📄 Verify by File Upload'}
              </h2>
              <p>
                {activeMethod === 'code' && 'Enter the verification code printed on the certificate.'}
                {activeMethod === 'index' && 'Enter your student index number to search the blockchain.'}
                {activeMethod === 'file' && 'Upload your certificate file to verify its authenticity.'}
              </p>
              
              {renderVerificationForm()}

              {error && (
                <div className="error-message">
                  <span>❌</span> {error}
                </div>
              )}
            </div>

            {renderMethodInfo()}
          </section>

          {/* Verification Result */}
          {result && result.valid && (
            result.method === 'code' ? renderDatabaseResult() : renderBlockchainResult()
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="verify-footer">
        <div className="footer-content">
          <p>© {new Date().getFullYear()} Department of Examinations, Sri Lanka</p>
          <p>This verification portal is for official use. Unauthorized use is prohibited.</p>
          <div className="footer-links">
            <a href="https://www.doenets.lk" target="_blank" rel="noopener noreferrer">Official Website</a>
            <span>|</span>
            <a href="#help">Help</a>
            <span>|</span>
            <a href="/login">Staff Login</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default VerifyPage;
