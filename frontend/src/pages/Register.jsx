import { useState } from 'react'
import { Code2 } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'

function Register() {
  const navigate = useNavigate()

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleRegister = async (event) => {
    event.preventDefault()
    setMessage('')
    setError('')
    setIsSubmitting(true)

    try {
      await api.post('/auth/register', {
        name,
        email,
        password,
      })

      setMessage('Account created successfully. Redirecting to login...')

      setTimeout(() => {
        navigate('/login')
      }, 800)
    } catch (err) {
      const detail = err.response?.data?.detail

      if (Array.isArray(detail)) {
        setError(detail[0]?.msg || 'Registration failed.')
      } else {
        setError(detail || 'Registration failed.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-left">
        <Link className="auth-brand" to="/">
          <span><Code2 size={21} /></span>
          <div><strong>AI Code Review</strong><small>Assistant</small></div>
        </Link>

        <span className="auth-eyebrow">Create your workspace</span>
        <h1>Create Your Account</h1>

        <p>
          Join AI Code Review Assistant and start analyzing your
          Python projects using AI and static analysis tools.
        </p>

        <ul>
          <li>Upload Python files</li>
          <li>Review code quality</li>
          <li>Track security reports</li>
          <li>Save review history</li>
        </ul>
      </div>

      <div className="auth-card">
        <h2>Register</h2>

        <form className="auth-form" onSubmit={handleRegister}>
          <label htmlFor="register-name">Full Name</label>
          <input
            id="register-name"
            name="name"
            placeholder="Your name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            autoComplete="name"
            required
          />

          <label htmlFor="register-email">Email</label>
          <input
            id="register-email"
            name="email"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />

          <label htmlFor="register-password">Password</label>
          <input
            id="register-password"
            name="password"
            type="password"
            placeholder="Password123"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="new-password"
            required
          />

          <p className="form-hint">
            Use at least 8 characters with letters and numbers.
          </p>

          {message && <p className="success-message">{message}</p>}
          {error && <p className="error-message">{error}</p>}

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="auth-switch-text">
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </section>
  )
}

export default Register
