import { NavLink, Outlet } from 'react-router-dom'

function MainLayout() {
  return (
    <div className="app-layout">
      <nav className="navbar">
        <div className="brand">
          <div className="brand-icon">AI</div>
          <div className="brand-text">Code Review Assistant</div>
        </div>

        <div className="nav-links">
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/upload">Upload Code</NavLink>
          <NavLink to="/login">Login</NavLink>
          <NavLink to="/register" className="nav-btn">Register</NavLink>
        </div>
      </nav>

      <Outlet />
    </div>
  )
}

export default MainLayout