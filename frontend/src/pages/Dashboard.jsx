import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'

function Dashboard() {
  const [uploads, setUploads] = useState([])

  useEffect(() => {
    const fetchUploads = async () => {
      try {
        const token = localStorage.getItem('token')

        if (!token) {
          return
        }

        const response = await api.get('/upload/history', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        setUploads(response.data)
      } catch (error) {
        console.error('Failed to fetch uploads:', error)
      }
    }

    fetchUploads()
  }, [])

  return (
    <section className="dashboard">
      <div className="hero-section">
        <div className="hero-content">
          <h1>
            AI-powered <span>code review</span> for better software.
          </h1>

          <p>
            Upload source code, detect bugs, identify security issues,
            analyze complexity, and receive AI-powered improvement suggestions.
          </p>

          <div className="hero-actions">
            <Link to="/upload" className="primary-btn">Start Review</Link>
            <Link to="/register" className="secondary-btn">Create Account</Link>
          </div>
        </div>

        <div className="hero-card">
          <div className="code-box">
            <p><span className="green">✓</span> Pylint code quality check</p>
            <p><span className="yellow">⚠</span> Bandit security scan</p>
            <p><span className="blue">↗</span> Radon complexity analysis</p>
            <p><span className="green">✓</span> AI review suggestions</p>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Reviews</h3>
          <p>0</p>
        </div>

        <div className="stat-card">
          <h3>Files Uploaded</h3>
          <p>{uploads.length}</p>
        </div>

        <div className="stat-card">
          <h3>Security Issues</h3>
          <p>0</p>
        </div>

        <div className="stat-card">
          <h3>AI Suggestions</h3>
          <p>0</p>
        </div>
      </div>

      <h2 className="section-title">Recent Uploads</h2>

      <div className="feature-grid">
        {uploads.length === 0 ? (
          <div className="feature-card">
            <h3>No uploads yet</h3>
            <p>Upload your first Python file to see it here.</p>
          </div>
        ) : (
          uploads.slice(0, 3).map((upload) => (
            <div className="feature-card" key={upload.id}>
              <h3>📄 {upload.filename}</h3>
              <p>Uploaded at: {new Date(upload.uploaded_at).toLocaleString()}</p>
            </div>
          ))
        )}
      </div>
    </section>
  )
}

export default Dashboard