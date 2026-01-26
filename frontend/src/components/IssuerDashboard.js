import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getDashboardStats, getPendingResults, issueCertificate, getCertificates } from '../services/api';
import './IssuerDashboard.css';

const IssuerDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [pendingResults, setPendingResults] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [issuing, setIssuing] = useState(null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboard') {
        const statsData = await getDashboardStats();
        setStats(statsData.stats);
      } else if (activeTab === 'pending') {
        const data = await getPendingResults();
        setPendingResults(data.results || []);
      } else if (activeTab === 'certificates') {
        const data = await getCertificates();
        setCertificates(data.certificates || []);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  const handleIssueCertificate = async (resultId) => {
    setIssuing(resultId);
    setMessage(null);
    
    try {
      const result = await issueCertificate(resultId);
      
      if (result.certificate) {
        setMessage({
          type: 'success',
          text: `Certificate issued successfully! Verification Code: ${result.verification_code}`
        });
        loadData();
      } else {
        setMessage({
          type: 'error',
          text: result.error || 'Failed to issue certificate'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Network error. Please try again.'
      });
    }
    
    setIssuing(null);
  };

  const viewCertificatePdf = (certificateId) => {
    const token = localStorage.getItem('token');
    window.open(
      `http://localhost:5000/api/certificates/${certificateId}/preview?token=${token}`,
      '_blank'
    );
  };

  const downloadCertificatePdf = (certificateId) => {
    const token = localStorage.getItem('token');
    // Create a temporary link to trigger download
    const link = document.createElement('a');
    link.href = `http://localhost:5000/api/certificates/${certificateId}/download?token=${token}`;
    link.download = '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">🏛️</div>
          <h2>DOE Sri Lanka</h2>
          <p>Certificate Issuing</p>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="nav-icon">📊</span>
            Dashboard
          </button>
          <button
            className={`nav-item ${activeTab === 'pending' ? 'active' : ''}`}
            onClick={() => setActiveTab('pending')}
          >
            <span className="nav-icon">📋</span>
            Pending Results
          </button>
          <button
            className={`nav-item ${activeTab === 'certificates' ? 'active' : ''}`}
            onClick={() => setActiveTab('certificates')}
          >
            <span className="nav-icon">📜</span>
            Issued Certificates
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">👤</div>
            <div className="user-details">
              <strong>{user?.full_name}</strong>
              <span>{user?.designation}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
            <button onClick={() => setMessage(null)}>×</button>
          </div>
        )}

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="tab-content">
            <h1>Dashboard</h1>
            <p className="subtitle">Certificate Issuing System Overview</p>

            {loading ? (
              <div className="loading">Loading...</div>
            ) : stats && (
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">👨‍🎓</div>
                  <div className="stat-value">{stats.total_students}</div>
                  <div className="stat-label">Total Students</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">📝</div>
                  <div className="stat-value">{stats.total_results}</div>
                  <div className="stat-label">Total Results</div>
                </div>
                <div className="stat-card warning">
                  <div className="stat-icon">⏳</div>
                  <div className="stat-value">{stats.pending_certification}</div>
                  <div className="stat-label">Pending Certification</div>
                </div>
                <div className="stat-card success">
                  <div className="stat-icon">✅</div>
                  <div className="stat-value">{stats.certificates_issued}</div>
                  <div className="stat-label">Certificates Issued</div>
                </div>
              </div>
            )}

            <div className="stats-grid secondary">
              <div className="stat-card small">
                <div className="stat-label">O/L Results</div>
                <div className="stat-value">{stats?.ol_results || 0}</div>
              </div>
              <div className="stat-card small">
                <div className="stat-label">A/L Results</div>
                <div className="stat-value">{stats?.al_results || 0}</div>
              </div>
            </div>
          </div>
        )}

        {/* Pending Results Tab */}
        {activeTab === 'pending' && (
          <div className="tab-content">
            <h1>Pending Results</h1>
            <p className="subtitle">Results awaiting certificate issuance</p>

            {loading ? (
              <div className="loading">Loading...</div>
            ) : pendingResults.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">✅</span>
                <p>No pending results. All certificates have been issued!</p>
              </div>
            ) : (
              <div className="results-table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Index Number</th>
                      <th>Student Name</th>
                      <th>Exam Type</th>
                      <th>Year</th>
                      <th>Subjects</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pendingResults.map((result) => (
                      <tr key={result.result_id}>
                        <td><strong>{result.index_number}</strong></td>
                        <td>{result.student?.full_name || 'N/A'}</td>
                        <td>
                          <span className={`badge ${result.exam_type === 'OL' ? 'badge-blue' : 'badge-purple'}`}>
                            G.C.E. {result.exam_type}
                          </span>
                        </td>
                        <td>{result.exam_year}</td>
                        <td>{result.subjects?.length || 0} subjects</td>
                        <td>
                          <span className="badge badge-yellow">Pending</span>
                        </td>
                        <td>
                          <button
                            className="issue-btn"
                            onClick={() => handleIssueCertificate(result.result_id)}
                            disabled={issuing === result.result_id}
                          >
                            {issuing === result.result_id ? 'Issuing...' : '📜 Issue Certificate'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Certificates Tab */}
        {activeTab === 'certificates' && (
          <div className="tab-content">
            <h1>Issued Certificates</h1>
            <p className="subtitle">All certificates that have been issued</p>

            {loading ? (
              <div className="loading">Loading...</div>
            ) : certificates.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📜</span>
                <p>No certificates have been issued yet.</p>
              </div>
            ) : (
              <div className="results-table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Certificate ID</th>
                      <th>Index Number</th>
                      <th>Exam</th>
                      <th>Year</th>
                      <th>Verification Code</th>
                      <th>Issued At</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {certificates.map((cert) => (
                      <tr key={cert.certificate_id}>
                        <td><code>{cert.certificate_id}</code></td>
                        <td><strong>{cert.index_number}</strong></td>
                        <td>
                          <span className={`badge ${cert.exam_type === 'OL' ? 'badge-blue' : 'badge-purple'}`}>
                            G.C.E. {cert.exam_type}
                          </span>
                        </td>
                        <td>{cert.exam_year}</td>
                        <td><code className="verification-code">{cert.verification_code}</code></td>
                        <td>{new Date(cert.issued_at).toLocaleDateString()}</td>
                        <td className="action-buttons">
                          <button
                            className="view-btn"
                            onClick={() => viewCertificatePdf(cert.certificate_id)}
                            title="View PDF in new tab"
                          >
                            👁️ View
                          </button>
                          <button
                            className="download-btn"
                            onClick={() => downloadCertificatePdf(cert.certificate_id)}
                            title="Download PDF"
                          >
                            📥 Download
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default IssuerDashboard;
