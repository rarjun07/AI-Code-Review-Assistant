import { Routes, Route } from 'react-router-dom'

import MainLayout from '../layouts/MainLayout'
import ProtectedRoute from './ProtectedRoute'
import Dashboard from '../pages/Dashboard'
import Login from '../pages/Login'
import Profile from '../pages/Profile'
import Register from '../pages/Register'
import ResetPassword from '../pages/ResetPassword'
import Upload from '../pages/Upload'
import NotFound from '../pages/NotFound'

import Reports from '../pages/Reports'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Dashboard />} />
        <Route
          path="upload"
          element={(
            <ProtectedRoute>
              <Upload />
            </ProtectedRoute>
          )}
        />
        <Route
          path="reports"
          element={(
            <ProtectedRoute>
              <Reports />
            </ProtectedRoute>
          )}
        />
        <Route
          path="profile"
          element={(
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          )}
        />
      </Route>
      
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/reset-password" element={<ResetPassword />} />

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default AppRoutes
