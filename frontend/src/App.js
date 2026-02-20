import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import IssuerDashboard from './components/IssuerDashboard';
import VerifyPage from './components/VerifyPage';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Redirect if already logged in
const PublicOnlyRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/issuer" replace />;
  }

  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<VerifyPage />} />
      <Route path="/verify" element={<VerifyPage />} />
      
      {/* Auth Routes */}
      <Route 
        path="/login" 
        element={
          <PublicOnlyRoute>
            <Login />
          </PublicOnlyRoute>
        } 
      />
      
      {/* Protected Issuer Routes */}
      <Route 
        path="/issuer" 
        element={
          <ProtectedRoute>
            <IssuerDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/issuer/*" 
        element={
          <ProtectedRoute>
            <IssuerDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* 404 Redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <AppRoutes />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
