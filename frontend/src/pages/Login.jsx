import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

function Login() {
  const navigate = useNavigate()

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
        navigate('/upload')
      }, 800)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed.')
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-left">
        <h1>Welcome Back 👋</h1>

        <p>
          Sign in to upload your source code, manage previous reviews,
          and receive AI-powered suggestions.
        </p>

        <ul>
          <li>✔ AI Code Review</li>
          <li>✔ Security Analysis</li>
          <li>✔ Code Quality Reports</li>
          <li>✔ Review History</li>
        </ul>
      </div>

      <div className="auth-card">
        <h2>Login</h2>

        <form className="auth-form" onSubmit={handleLogin}>
          <label>Email</label>
          <input
            type="email"
            placeholder="Enter email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {message && <p className="success-message">{message}</p>}
          {error && <p className="error-message">{error}</p>}

          <button type="submit">
            Login
          </button>
        </form>
      </div>
    </section>
  )
}

export default Login