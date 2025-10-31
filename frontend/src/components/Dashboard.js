import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || '/api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, healthRes] = await Promise.all([
        axios.get(`${API_URL}/stats`),
        axios.get(`${API_URL}/health`)
      ]);
      setStats(statsRes.data);
      setHealth(healthRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>{stats?.users || 0}</h3>
          <p>Total Users</p>
        </div>
        <div className="stat-card">
          <h3>{stats?.products || 0}</h3>
          <p>Total Products</p>
        </div>
        <div className="stat-card">
          <h3>{health?.status === 'healthy' ? '✓' : '✗'}</h3>
          <p>System Status</p>
        </div>
      </div>

      <div className="card">
        <h2>System Information</h2>
        <table className="table">
          <tbody>
            <tr>
              <td><strong>Backend Version</strong></td>
              <td>{health?.version || 'N/A'}</td>
            </tr>
            <tr>
              <td><strong>Database Status</strong></td>
              <td>{health?.database || 'N/A'}</td>
            </tr>
            <tr>
              <td><strong>Redis Status</strong></td>
              <td>{health?.redis || 'N/A'}</td>
            </tr>
            <tr>
              <td><strong>Last Check</strong></td>
              <td>{health?.timestamp ? new Date(health.timestamp * 1000).toLocaleString() : 'N/A'}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>🚀 Welcome to DevOps Microservices Platform</h2>
        <p>
          This is a demonstration platform showcasing a complete DevOps workflow with:
        </p>
        <ul style={{ marginLeft: '2rem', marginTop: '1rem', lineHeight: '2' }}>
          <li>✅ Microservices Architecture (Flask Backend + React Frontend)</li>
          <li>✅ Docker Containerization</li>
          <li>✅ Kubernetes Orchestration</li>
          <li>✅ CI/CD Pipeline (Jenkins & GitLab CI)</li>
          <li>✅ Monitoring with Prometheus & Grafana</li>
          <li>✅ Automated Testing</li>
        </ul>
      </div>
    </div>
  );
}

export default Dashboard;
