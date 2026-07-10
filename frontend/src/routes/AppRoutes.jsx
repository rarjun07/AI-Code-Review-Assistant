import { Routes, Route } from 'react-router-dom'

import MainLayout from '../layouts/MainLayout'
import Dashboard from '../pages/Dashboard'
import Login from '../pages/Login'
import Register from '../pages/Register'
import Upload from '../pages/Upload'
import NotFound from '../pages/NotFound'

import Reports from '../pages/Reports'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="upload" element={<Upload />} />
        <Route path="reports" element={<Reports />} />
      </Route>
      
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default AppRoutes