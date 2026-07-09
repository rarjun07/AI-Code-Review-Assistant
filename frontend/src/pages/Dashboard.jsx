import { Link } from 'react-router-dom'

function Dashboard() {
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
          <p>0</p>
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

      <h2 className="section-title">Analysis Features</h2>

      <div className="feature-grid">
        <div className="feature-card">
          <h3>📊 Code Quality</h3>
          <p>Analyze coding standards, unused variables, syntax issues, and maintainability using Pylint.</p>
        </div>

        <div className="feature-card">
          <h3>🛡 Security Scan</h3>
          <p>Detect common security vulnerabilities using Bandit before your code reaches production.</p>
        </div>

        <div className="feature-card">
          <h3>📈 Complexity</h3>
          <p>Measure cyclomatic complexity and maintainability index using Radon.</p>
        </div>

        <div className="feature-card">
          <h3>🤖 AI Review</h3>
          <p>Generate bug reports, refactoring suggestions, naming improvements, and best practices.</p>
        </div>

        <div className="feature-card">
          <h3>📑 Review History</h3>
          <p>View previous reviews, detailed findings, and structured analysis reports.</p>
        </div>

        <div className="feature-card">
          <h3>🔐 Secure Access</h3>
          <p>JWT authentication keeps accounts and code review history protected.</p>
        </div>
      </div>
    </section>
  )
}

export default Dashboard