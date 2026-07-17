import { useState } from 'react'
import { Code2 } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import api from '../services/api'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setMessage('')
    setError('')

    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response = await api.post('/auth/login', formData)

      localStorage.setItem('token', response.data.access_token)

      setMessage('Login successful! Redirecting...')
      setTimeout(() => {
        navigate(location.state?.from || '/upload', { replace: true })
      }, 800)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed.')
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-left">
        <Link className="auth-brand" to="/">
          <span><Code2 size={21} /></span>
          <div><strong>CodeLens AI</strong><small>Review Assistant</small></div>
        </Link>

        <span className="auth-eyebrow">Developer workspace</span>
        <h1>Welcome back.</h1>

        <p>
          Sign in to upload your source code, manage previous reviews,
          and receive AI-powered suggestions.
        </p>

        <ul>
          <li>AI-powered code review</li>
          <li>Security and complexity analysis</li>
          <li>Structured quality reports</li>
          <li>Searchable review history</li>
        </ul>
      </div>

      <div className="auth-card">
        <h2>Login</h2>

        <form className="auth-form" onSubmit={handleLogin}>
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            name="email"
            type="email"
            placeholder="Enter email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />

          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            name="password"
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />

          {message && <p className="success-message">{message}</p>}
          {error && <p className="error-message">{error}</p>}

          <button type="submit">
            Login
          </button>
        </form>

        <Link className="auth-link" to="/reset-password">
          Forgot password?
        </Link>

        <p className="auth-switch-text">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </div>
    </section>
  )
}

export default Login
