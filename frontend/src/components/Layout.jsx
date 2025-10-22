// src/components/Layout.jsx - Main layout with navigation
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

const Layout = () => {
  return (
    <div className="flex h-screen bg-arcade-beige">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Page content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-arcade-beige">
          <div className="p-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout

