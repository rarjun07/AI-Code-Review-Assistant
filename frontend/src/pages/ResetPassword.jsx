import { useState } from 'react'
import { Code2 } from 'lucide-react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import api from '../services/api'

function ResetPassword() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [email, setEmail] = useState('')
  const [resetToken, setResetToken] = useState(
    searchParams.get('token') || ''
  )
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleResetRequest = async (event) => {
    event.preventDefault()
    setMessage('')
    setError('')
    setIsSubmitting(true)

    try {
      const response = await api.post('/auth/password-reset/request', {
        email,
      })

      if (response.data.reset_token) {
        setResetToken(response.data.reset_token)
        setMessage('Local reset link created. Choose a new password.')
      } else {
        setMessage(response.data.message)
      }
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(Array.isArray(detail) ? detail[0]?.msg : detail || 'Request failed.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleResetPassword = async (event) => {
    event.preventDefault()
    setMessage('')
    setError('')

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setIsSubmitting(true)

    try {
      await api.post('/auth/password-reset/confirm', {
        reset_token: resetToken,
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
          <div><strong>AI Code Review</strong><small>Assistant</small></div>
        </Link>

        <span className="auth-eyebrow">Account recovery</span>
        <h1>Reset Password</h1>

        <p>
          Request a protected, time-limited recovery link before choosing
          a new password for your account.
        </p>

        <ul>
          <li>Use at least 8 characters</li>
          <li>Include letters and numbers</li>
          <li>Login again after reset</li>
        </ul>
      </div>

      <div className="auth-card">
        <h2>{resetToken ? 'New Password' : 'Recover Account'}</h2>

        {!resetToken ? (
          <form className="auth-form" onSubmit={handleResetRequest}>
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

            {message && <p className="success-message">{message}</p>}
            {error && <p className="error-message">{error}</p>}

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Creating link...' : 'Request Reset Link'}
            </button>
          </form>
        ) : (
          <form className="auth-form" onSubmit={handleResetPassword}>
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

            <label htmlFor="confirm-reset-password">Confirm Password</label>
            <input
              id="confirm-reset-password"
              name="confirm-password"
              type="password"
              placeholder="Repeat new password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
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
        )}

        <Link className="auth-link" to="/login">
          Back to login
        </Link>
      </div>
    </section>
  )
}

export default ResetPassword
