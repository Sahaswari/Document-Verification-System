import React, { useState } from 'react';
import { verifyCertificate } from '../services/api';
import './VerifyPage.css';

const VerifyPageEnhanced = () => {
  // Verification method selection
  const [verificationMethod, setVerificationMethod] = useState('code'); // code, hash, index, file
  
  // Form inputs
  const [verificationCode, setVerificationCode] = useState('');
  const [documentHash, setDocumentHash] = useState('');
  const [studentIndex, setStudentIndex] = useState('');
  const [certificateFile, setCertificateFile] = useState(null);
  
  // State
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
      if (!allowedTypes.includes(file.type)) {
        setError('Invalid file type. Please upload PDF, JPG, or PNG file.');
        setCertificateFile(null);
        return;
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File too large. Maximum size is 10MB.');
        setCertificateFile(null);
        return;
      }
      
      setCertificateFile(file);
      setError(null);
    }
  };

  // Handle verification based on selected method
  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let data;
      
      switch (verificationMethod) {
        case 'code':
          // Verify by verification code (existing database method)
          if (!verificationCode.trim()) {
            setError('Please enter a verification code');
            setLoading(false);
            return;
          }
          data = await verifyCertificate(verificationCode.trim());
          break;
          
        case 'hash':
          // Verify by document hash (blockchain)
          if (!documentHash.trim()) {
            setError('Please enter a document hash');
            setLoading(false);
            return;
          }
          
          // Validate hash format (64 hex characters)
          if (!/^[a-fA-F0-9]{64}$/.test(documentHash.trim())) {
            setError('Invalid hash format. Must be 64 hexadecimal characters.');
            setLoading(false);
            return;
          }
          
          const hashResponse = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/certificate/verify-by-hash`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ document_hash: documentHash.trim() })
          });
          data = await hashResponse.json();
          
          // Transform blockchain response to match UI format
          if (data.verified) {
            data = {
              valid: true,
              certificate: {
                ...data.details,
                result: {
                  exam_type: data.details.documentType || data.details.document_type,
                  exam_year: data.details.examYear || data.details.exam_year,
                  index_number: data.details.studentIndex || data.details.student_index,
                  subjects: [] // Blockchain doesn't store individual subjects
                },
                student: {
                  full_name: 'Verified on Blockchain',
                  school_name: 'N/A'
                },
                document_hash: documentHash.trim()
              }
            };
          } else {
            setError('Certificate not found on blockchain or has been revoked');
            setLoading(false);
            return;
          }
          break;
          
        case 'index':
          // Verify by student index (blockchain)
          if (!studentIndex.trim()) {
            setError('Please enter a student index number');
            setLoading(false);
            return;
          }
          
          const indexResponse = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/certificate/verify-by-index`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_index: studentIndex.trim() })
          });
          data = await indexResponse.json();
          
          // Transform blockchain response
          if (data.verified) {
            data = {
              valid: true,
              certificate: {
                ...data.details,
                result: {
                  exam_type: data.details.documentType || data.details.document_type,
                  exam_year: data.details.examYear || data.details.exam_year,
                  index_number: studentIndex.trim(),
                  subjects: []
                },
                student: {
                  full_name: 'Verified on Blockchain',
                  school_name: 'N/A'
                },
                document_hash: data.details.documentHash || data.details.document_hash
              }
            };
          } else {
            setError(data.message || 'Certificate not found for this student index');
            setLoading(false);
            return;
          }
          break;
          
        case 'file':
          // Verify by uploading file (blockchain via hash)
          if (!certificateFile) {
            setError('Please select a certificate file to upload');
            setLoading(false);
            return;
          }
          
          const formData = new FormData();
          formData.append('certificate', certificateFile);
          
          const fileResponse = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/certificate/verify`, {
            method: 'POST',
            body: formData
          });
          data = await fileResponse.json();
          
          // Transform blockchain response
          if (data.verified && data.exists) {
            data = {
              valid: true,
              certificate: {
                ...data.certificate_details,
                result: {
                  exam_type: data.certificate_details.document_type,
                  exam_year: data.certificate_details.exam_year,
                  index_number: data.certificate_details.student_index,
                  subjects: []
                },
                student: {
                  full_name: 'Verified on Blockchain',
                  school_name: 'N/A'
                },
                document_hash: data.certificate_details.document_hash
              }
            };
          } else {
            setError(data.message || data.warning || 'Certificate not found or invalid');
            setLoading(false);
            return;
          }
          break;
          
        default:
          setError('Invalid verification method');
          setLoading(false);
          return;
      }
      
      // Handle response
      if (data.valid || data.verified) {
        setResult(data);
      } else {
        setError(data.message || 'Certificate not found or invalid');
      }
    } catch (err) {
      console.error('Verification error:', err);
      setError('Network error. Please try again.');
    }

    setLoading(false);
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

  return (
    <div className="verify-page">
      {/* Header */}
      <header className="verify-header">
        <div className="header-content">
          <div className="emblem">🇱🇰</div>
          <div className="header-text">
            <h1>Department of Examinations - Sri Lanka</h1>
            <p>G.C.E. Certificate Verification Portal (Blockchain-Powered)</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="verify-main">
        <div className="verify-container">
          {/* Verification Method Selection */}
          <section className="method-selection">
            <h3>Choose Verification Method:</h3>
            <div className="method-tabs">
              <button 
                className={verificationMethod === 'code' ? 'active' : ''}
                onClick={() => {
                  setVerificationMethod('code');
                  setError(null);
                  setResult(null);
                }}
              >
                📋 Verification Code
              </button>
              <button 
                className={verificationMethod === 'index' ? 'active' : ''}
                onClick={() => {
                  setVerificationMethod('index');
                  setError(null);
                  setResult(null);
                }}
              >
                🎓 Student Index
              </button>
              <button 
                className={verificationMethod === 'file' ? 'active' : ''}
                onClick={() => {
                  setVerificationMethod('file');
                  setError(null);
                  setResult(null);
                }}
              >
                📄 Upload Certificate
              </button>
              <button 
                className={verificationMethod === 'hash' ? 'active' : ''}
                onClick={() => {
                  setVerificationMethod('hash');
                  setError(null);
                  setResult(null);
                }}
              >
                🔗 Blockchain Hash
              </button>
            </div>
          </section>

          {/* Verification Form */}
          <section className="verify-form-section">
            <div className="form-card">
              <h2>🔍 Verify Certificate</h2>
              
              {/* Method-specific forms */}
              <form onSubmit={handleVerify}>
                
                {/* Method 1: Verification Code */}
                {verificationMethod === 'code' && (
                  <>
                    <p>Enter the verification code printed on the certificate.</p>
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
                      <small>Format: DOE-OL/AL-YEAR-XXXXXXXX</small>
                    </div>
                  </>
                )}

                {/* Method 2: Document Hash */}
                {verificationMethod === 'hash' && (
                  <>
                    <p>Enter the SHA-256 document hash from the blockchain.</p>
                    <div className="input-group">
                      <label htmlFor="hash">Document Hash</label>
                      <input
                        type="text"
                        id="hash"
                        placeholder="e.g., a1b2c3d4e5f6... (64 characters)"
                        value={documentHash}
                        onChange={(e) => setDocumentHash(e.target.value.toLowerCase())}
                        className={error ? 'input-error' : ''}
                        maxLength="64"
                      />
                      <small>64 hexadecimal characters (SHA-256 hash)</small>
                    </div>
                  </>
                )}

                {/* Method 3: Student Index */}
                {verificationMethod === 'index' && (
                  <>
                    <p>Enter the student's index number from the examination.</p>
                    <div className="input-group">
                      <label htmlFor="index">Student Index Number</label>
                      <input
                        type="text"
                        id="index"
                        placeholder="e.g., 2023OL123456 or 2023AL987654"
                        value={studentIndex}
                        onChange={(e) => setStudentIndex(e.target.value.toUpperCase())}
                        className={error ? 'input-error' : ''}
                      />
                      <small>Format: YEAR + OL/AL + 6 digits</small>
                    </div>
                  </>
                )}

                {/* Method 4: Upload File */}
                {verificationMethod === 'file' && (
                  <>
                    <p>Upload the certificate PDF or image file for verification.</p>
                    <div className="input-group">
                      <label htmlFor="file">Certificate File</label>
                      <input
                        type="file"
                        id="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        onChange={handleFileChange}
                        className={error ? 'input-error' : ''}
                      />
                      <small>Accepted: PDF, JPG, PNG (Max 10MB)</small>
                      {certificateFile && (
                        <div className="file-info">
                          ✓ Selected: {certificateFile.name} ({(certificateFile.size / 1024).toFixed(2)} KB)
                        </div>
                      )}
                    </div>
                  </>
                )}
                
                <button type="submit" disabled={loading} className="verify-btn">
                  {loading ? '⏳ Verifying...' : '✓ Verify Certificate'}
                </button>
              </form>

              {error && (
                <div className="error-message">
                  <span>❌</span> {error}
                </div>
              )}
            </div>

            {/* Info Card */}
            <div className="info-card">
              <h3>ℹ️ About This Method</h3>
              {verificationMethod === 'code' && (
                <p>The verification code is printed at the bottom of official certificates. This method queries the Department's database and blockchain for fastest results.</p>
              )}
              {verificationMethod === 'hash' && (
                <p>The document hash is the SHA-256 fingerprint stored on the blockchain. This method directly queries the smart contract for verification.</p>
              )}
              {verificationMethod === 'index' && (
                <p>Every student has a unique index number assigned during examination. This method finds the certificate registered under that index on the blockchain.</p>
              )}
              {verificationMethod === 'file' && (
                <p>Upload your certificate file. The system will calculate its hash and verify it against the blockchain. This ensures the file hasn't been tampered with.</p>
              )}
              
              <div className="blockchain-badge">
                <span>🔗</span>
                <strong>Blockchain-Verified</strong>
                <p>All certificates are cryptographically secured on Ethereum blockchain</p>
              </div>
            </div>
          </section>

          {/* Verification Result (same as before) */}
          {result && (
            <section className="result-section">
              <div className="result-card valid">
                <div className="result-header">
                  <div className="valid-badge">
                    <span className="checkmark">✓</span>
                    <span>VERIFIED</span>
                  </div>
                  <p>This certificate is authentic and registered on the blockchain.</p>
                </div>

                <div className="certificate-details">
                  {/* Student Information */}
                  {result.certificate.student && (
                    <div className="detail-group">
                      <h4>Student Information</h4>
                      <div className="detail-row">
                        <span className="label">Full Name</span>
                        <span className="value">{result.certificate.student.full_name || 'Verified on Blockchain'}</span>
                      </div>
                      {result.certificate.student.date_of_birth && (
                        <div className="detail-row">
                          <span className="label">Date of Birth</span>
                          <span className="value">{result.certificate.student.date_of_birth}</span>
                        </div>
                      )}
                      {result.certificate.student.school_name && result.certificate.student.school_name !== 'N/A' && (
                        <div className="detail-row">
                          <span className="label">School</span>
                          <span className="value">{result.certificate.student.school_name}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Examination Details */}
                  <div className="detail-group">
                    <h4>Examination Details</h4>
                    <div className="detail-row">
                      <span className="label">Examination</span>
                      <span className="value">
                        <span className={`exam-badge ${result.certificate.result.exam_type === 'OL' || result.certificate.result.exam_type === 'O/L' ? 'ol' : 'al'}`}>
                          G.C.E. {result.certificate.result.exam_type === 'OL' || result.certificate.result.exam_type === 'O/L' ? 'Ordinary Level' : 'Advanced Level'}
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
                  </div>
                </div>

                {/* Subject Results (if available) */}
                {result.certificate.result.subjects && result.certificate.result.subjects.length > 0 && (
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
                )}

                {/* Blockchain Info */}
                <div className="blockchain-section">
                  <h4>🔗 Blockchain Verification</h4>
                  <div className="blockchain-info">
                    <div className="detail-row">
                      <span className="label">Document Hash</span>
                      <span className="value hash"><code>{result.certificate.document_hash}</code></span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Verification Method</span>
                      <span className="value">
                        {verificationMethod === 'code' && 'Database + Blockchain'}
                        {verificationMethod === 'hash' && 'Direct Blockchain Query'}
                        {verificationMethod === 'index' && 'Blockchain Index Lookup'}
                        {verificationMethod === 'file' && 'File Hash + Blockchain'}
                      </span>
                    </div>
                    {result.certificate.issued_at && (
                      <div className="detail-row">
                        <span className="label">Issued On</span>
                        <span className="value">{new Date(result.certificate.issued_at).toLocaleString()}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </section>
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

export default VerifyPageEnhanced;
