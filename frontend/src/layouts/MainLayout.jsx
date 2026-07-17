import { useEffect, useRef, useState } from 'react'
import {
  Activity,
  ChevronDown,
  Code2,
  FileSearch,
  LayoutDashboard,
  LogIn,
  LogOut,
  Menu,
  Search,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  UserRound,
  UserPlus,
  X,
} from 'lucide-react'
import {
  NavLink,
  Outlet,
  useLocation,
  useNavigate,
} from 'react-router-dom'
import api from '../services/api'

const pageDetails = {
  '/': {
    eyebrow: 'Workspace',
    title: 'Review dashboard',
  },
  '/upload': {
    eyebrow: 'Analysis',
    title: 'New code review',
  },
  '/reports': {
    eyebrow: 'Review library',
    title: 'Saved reports',
  },
  '/profile': {
    eyebrow: 'Account',
    title: 'Profile settings',
  },
}

function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const profileMenuRef = useRef(null)
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false)
  const [isNavigationOpen, setIsNavigationOpen] = useState(false)
  const [user, setUser] = useState(null)
  const isAuthenticated = Boolean(localStorage.getItem('token'))
  const currentPage = pageDetails[location.pathname] || pageDetails['/']

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        profileMenuRef.current &&
        !profileMenuRef.current.contains(event.target)
      ) {
        setIsProfileMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  useEffect(() => {
    if (!isAuthenticated) {
      return
    }

    const loadUser = async () => {
      try {
        const response = await api.get('/auth/me', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        })
        setUser(response.data)
      } catch {
        setUser(null)
      }
    }

    loadUser()
  }, [isAuthenticated])

  const closeNavigation = () => {
    setIsNavigationOpen(false)
    setIsProfileMenuOpen(false)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    closeNavigation()
    navigate('/login')
  }

  const handleSearch = (event) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const query = String(form.get('search') || '').trim()
    navigate(query ? `/reports?search=${encodeURIComponent(query)}` : '/reports')
  }

  const initials = user?.name
    ? user.name
        .split(' ')
        .slice(0, 2)
        .map((part) => part[0])
        .join('')
        .toUpperCase()
    : 'AI'

  return (
    <div className="app-shell">
      <aside className={`app-sidebar ${isNavigationOpen ? 'app-sidebar-open' : ''}`}>
        <NavLink
          to="/"
          className="brand"
          aria-label="AI Code Review Assistant home"
          onClick={closeNavigation}
        >
          <span className="brand-icon"><Code2 size={22} /></span>
          <span className="brand-copy">
            <strong>CodeLens AI</strong>
            <small>Review Assistant</small>
          </span>
        </NavLink>

        <div className="sidebar-workspace">
          <span className="workspace-mark"><Sparkles size={16} /></span>
          <span>
            <small>Current workspace</small>
            <strong>Python reviews</strong>
          </span>
        </div>

        <nav className="sidebar-nav" aria-label="Primary navigation">
          <p className="sidebar-label">Overview</p>
          <NavLink to="/" end onClick={closeNavigation}>
            <LayoutDashboard size={19} />
            <span>Dashboard</span>
          </NavLink>

          {isAuthenticated && (
            <>
              <p className="sidebar-label">Code review</p>
              <NavLink to="/upload" onClick={closeNavigation}>
                <UploadCloud size={19} />
                <span>New review</span>
              </NavLink>
              <NavLink to="/reports" onClick={closeNavigation}>
                <FileSearch size={19} />
                <span>Report library</span>
              </NavLink>

              <p className="sidebar-label">Account</p>
              <NavLink to="/profile" onClick={closeNavigation}>
                <UserRound size={19} />
                <span>Profile settings</span>
              </NavLink>
            </>
          )}
        </nav>

        <div className="sidebar-spacer" />

        <div className="engine-status">
          <span className="engine-status-icon"><Activity size={18} /></span>
          <span>
            <strong>Analysis engine</strong>
            <small><i /> Ready for Python</small>
          </span>
        </div>

        {isAuthenticated ? (
          <button className="sidebar-logout" type="button" onClick={handleLogout}>
            <LogOut size={18} />
            Sign out
          </button>
        ) : (
          <div className="sidebar-auth-actions">
            <NavLink to="/login" onClick={closeNavigation}>
              <LogIn size={18} /> Sign in
            </NavLink>
            <NavLink to="/register" onClick={closeNavigation}>
              <UserPlus size={18} /> Create account
            </NavLink>
          </div>
        )}
      </aside>

      {isNavigationOpen && (
        <button
          className="sidebar-overlay"
          type="button"
          aria-label="Close navigation"
          onClick={closeNavigation}
        />
      )}

      <main className="app-main">
        <header className="app-topbar">
          <button
            className="mobile-nav-toggle"
            type="button"
            aria-label={isNavigationOpen ? 'Close navigation' : 'Open navigation'}
            aria-expanded={isNavigationOpen}
            onClick={() => setIsNavigationOpen((isOpen) => !isOpen)}
          >
            {isNavigationOpen ? <X size={22} /> : <Menu size={22} />}
          </button>

          <div className="topbar-title">
            <span>{currentPage.eyebrow}</span>
            <h1>{currentPage.title}</h1>
          </div>

          {isAuthenticated && (
            <form className="global-search" role="search" onSubmit={handleSearch}>
              <Search size={18} />
              <input
                name="search"
                type="search"
                placeholder="Search reports"
                aria-label="Search saved reports"
              />
              <kbd>↵</kbd>
            </form>
          )}

          <div className="topbar-status" title="Security checks enabled">
            <ShieldCheck size={18} />
            <span>Protected</span>
          </div>

          {isAuthenticated ? (
            <div className="profile-menu" ref={profileMenuRef}>
              <button
                className="profile-chip"
                type="button"
                aria-label="Open account menu"
                aria-expanded={isProfileMenuOpen}
                onClick={() => setIsProfileMenuOpen((isOpen) => !isOpen)}
              >
                <span className="profile-avatar">{initials}</span>
                <span className="profile-chip-copy">
                  <strong>{user?.name || 'Developer'}</strong>
                  <small>{user?.email || 'Signed in'}</small>
                </span>
                <ChevronDown size={16} />
              </button>

              {isProfileMenuOpen && (
                <div className="profile-dropdown">
                  <div className="profile-dropdown-identity">
                    <span className="profile-avatar">{initials}</span>
                    <span>
                      <strong>{user?.name || 'Developer'}</strong>
                      <small>{user?.email || 'AI Code Review account'}</small>
                    </span>
                  </div>
                  <NavLink to="/profile" onClick={closeNavigation}>
                    <UserRound size={17} /> Profile settings
                  </NavLink>
                  <button type="button" onClick={handleLogout}>
                    <LogOut size={17} /> Sign out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="topbar-auth-actions">
              <NavLink to="/login">Sign in</NavLink>
              <NavLink to="/register">Get started</NavLink>
            </div>
          )}
        </header>

        <div className="app-content">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default MainLayout
