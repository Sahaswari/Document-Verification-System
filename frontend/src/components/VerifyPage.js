import React, { useState } from 'react';
import { verifyCertificate } from '../services/api';
import './VerifyPage.css';

const VerifyPage = () => {
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleVerify = async (e) => {
    e.preventDefault();
    
    if (!verificationCode.trim()) {
      setError('Please enter a verification code');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await verifyCertificate(verificationCode.trim());
      
      if (data.valid) {
        setResult(data);
      } else {
        setError(data.message || 'Certificate not found or invalid');
      }
    } catch (err) {
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
            <p>G.C.E. Certificate Verification Portal</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="verify-main">
        <div className="verify-container">
          {/* Verification Form */}
          <section className="verify-form-section">
            <div className="form-card">
              <h2>🔍 Verify Certificate</h2>
              <p>Enter the verification code printed on the certificate to verify its authenticity.</p>
              
              <form onSubmit={handleVerify}>
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

              {error && (
                <div className="error-message">
                  <span>❌</span> {error}
                </div>
              )}
            </div>

            <div className="info-card">
              <h3>ℹ️ How to find the verification code?</h3>
              <p>The verification code is located at the bottom of your certificate, below the QR code. It starts with "DOE-" followed by the exam type and a unique identifier.</p>
              <div className="example-code">
                Example: <code>DOE-OL2023-A1B2C3D4</code>
              </div>
            </div>
          </section>

          {/* Verification Result */}
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

                {/* Blockchain Info */}
                <div className="blockchain-section">
                  <h4>🔗 Blockchain Verification</h4>
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
