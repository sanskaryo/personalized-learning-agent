// src/App.jsx - Main App component with routing
import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Progress from './pages/Progress'
import Profile from './pages/Profile'
import Timer from './pages/Timer'
import Resources from './pages/Resources'
import PDFChat from './pages/PDFChat'
import Planner from './pages/Planner'
import Notes from './pages/Notes'

function App() {
  const { isAuthenticated, initializeAuth } = useAuthStore()
  
  // Initialize auth on app load
  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  return (
    <div className="min-h-screen bg-arcade-beige">
      <Routes>
        {/* Public routes */}
        <Route 
          path="/login" 
          element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} 
        />
        <Route 
          path="/register" 
          element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} 
        />
        
        {/* Protected routes */}
        <Route 
          path="/" 
          element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}
        >
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="chat" element={<Chat />} />
          <Route path="progress" element={<Progress />} />
          <Route path="profile" element={<Profile />} />
          {/* New routes for sidebar navigation */}
          <Route path="planner" element={<Planner />} />
          <Route path="resources" element={<Resources />} />
          <Route path="scriba" element={<PDFChat />} />
          <Route path="timer" element={<Timer />} />
          <Route path="notes" element={<Notes />} />
        </Route>
        
        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  )
}

export default App

