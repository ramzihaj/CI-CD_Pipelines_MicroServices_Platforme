import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css';
import Users from './components/Users';
import Products from './components/Products';
import Dashboard from './components/Dashboard';

const API_URL = process.env.REACT_APP_API_URL || '/api';

function App() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`);
      setHealth(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealth({ status: 'unhealthy', error: error.message });
      setLoading(false);
    }
  };

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <div className="container">
            <h1>🚀 DevOps Microservices Platform</h1>
            <nav className="nav">
              <Link to="/" className="nav-link">Dashboard</Link>
              <Link to="/users" className="nav-link">Users</Link>
              <Link to="/products" className="nav-link">Products</Link>
            </nav>
            <div className="health-status">
              {loading ? (
                <span className="status-badge loading">Checking...</span>
              ) : health?.status === 'healthy' ? (
                <span className="status-badge healthy">✓ System Healthy</span>
              ) : (
                <span className="status-badge unhealthy">✗ System Unhealthy</span>
              )}
            </div>
          </div>
        </header>

        <main className="App-main">
          <div className="container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/users" element={<Users />} />
              <Route path="/products" element={<Products />} />
            </Routes>
          </div>
        </main>

        <footer className="App-footer">
          <div className="container">
            <p>DevOps Cloud Platform - CI/CD Pipeline Demo</p>
            <p>Backend: Flask | Frontend: React | Orchestration: Kubernetes</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
