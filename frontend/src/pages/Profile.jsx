import { useEffect, useState } from 'react'
import { ShieldCheck, Sparkles, UserRound } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

function Profile() {
  const navigate = useNavigate()

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [createdAt, setCreatedAt] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    const loadProfile = async () => {
      const token = localStorage.getItem('token')

      if (!token) {
        navigate('/login')
        return
      }

      try {
        const response = await api.get('/auth/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        setName(response.data.name)
        setEmail(response.data.email)
        setCreatedAt(response.data.created_at)
      } catch (err) {
        setError(err.response?.data?.detail || 'Profile could not be loaded.')
      }
    }

    loadProfile()
  }, [navigate])

  const handleUpdateProfile = async (event) => {
    event.preventDefault()
    setMessage('')
    setError('')
    setIsSaving(true)

    const token = localStorage.getItem('token')

    try {
      const response = await api.put(
        '/auth/profile',
        {
          name,
          email,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      setName(response.data.name)
      setEmail(response.data.email)
      setMessage('Profile updated successfully.')
    } catch (err) {
      const detail = err.response?.data?.detail

      if (Array.isArray(detail)) {
        setError(detail[0]?.msg || 'Profile update failed.')
      } else {
        setError(detail || 'Profile update failed.')
      }
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <section className="profile-page">
      <header className="page-intro">
        <div>
          <span className="page-kicker"><Sparkles size={15} /> Account settings</span>
          <h2>Keep your developer profile up to date.</h2>
          <p>Your profile identifies the owner of saved reviews and analysis history.</p>
        </div>
        <span className="page-intro-badge"><ShieldCheck size={17} /> Protected account</span>
      </header>

      <div className="profile-panel">
        <div className="profile-header">
          <span className="profile-panel-icon"><UserRound size={24} /></span>
          <div><h2>Personal information</h2><p>Update your account name and email address.</p></div>
        </div>

        {createdAt && (
          <p className="profile-meta">
            Account created: {new Date(createdAt).toLocaleString()}
          </p>
        )}

        <form className="auth-form" onSubmit={handleUpdateProfile}>
          <label htmlFor="profile-name">Full Name</label>
          <input
            id="profile-name"
            name="name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            autoComplete="name"
            required
          />

          <label htmlFor="profile-email">Email</label>
          <input
            id="profile-email"
            name="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />

          {message && <p className="feedback-message feedback-success">{message}</p>}
          {error && <p className="feedback-message feedback-error">{error}</p>}

          <button type="submit" disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Update Profile'}
          </button>
        </form>
      </div>
    </section>
  )
}

export default Profile
