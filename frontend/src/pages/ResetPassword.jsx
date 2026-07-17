import { useState } from 'react'
import { Code2 } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'

function ResetPassword() {
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleResetPassword = async (event) => {
    event.preventDefault()
    setMessage('')
    setError('')
    setIsSubmitting(true)

    try {
      await api.post('/auth/reset-password', {
        email,
        new_password: newPassword,
      })

      setMessage('Password reset successfully. Redirecting to login...')

      setTimeout(() => {
        navigate('/login')
      }, 900)
    } catch (err) {
      const detail = err.response?.data?.detail

      if (Array.isArray(detail)) {
        setError(detail[0]?.msg || 'Password reset failed.')
      } else {
        setError(detail || 'Password reset failed.')
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
          <div><strong>CodeLens AI</strong><small>Review Assistant</small></div>
        </Link>

        <span className="auth-eyebrow">Account recovery</span>
        <h1>Reset Password</h1>

        <p>
          Enter your account email and choose a new password for your
          AI Code Review Assistant account.
        </p>

        <ul>
          <li>Use at least 8 characters</li>
          <li>Include letters and numbers</li>
          <li>Login again after reset</li>
        </ul>
      </div>

      <div className="auth-card">
        <h2>New Password</h2>

        <form className="auth-form" onSubmit={handleResetPassword}>
          <label htmlFor="reset-email">Email</label>
          <input
            id="reset-email"
            name="email"
            type="email"
            placeholder="Enter email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />

          <label htmlFor="reset-password">New Password</label>
          <input
            id="reset-password"
            name="new-password"
            type="password"
            placeholder="Password123"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            autoComplete="new-password"
            required
          />

          <p className="form-hint">
            Use at least 8 characters with letters and numbers.
          </p>

          {message && <p className="success-message">{message}</p>}
          {error && <p className="error-message">{error}</p>}

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>

        <Link className="auth-link" to="/login">
          Back to login
        </Link>
      </div>
    </section>
  )
}

export default ResetPassword
