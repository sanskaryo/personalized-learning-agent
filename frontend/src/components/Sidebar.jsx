// src/components/Sidebar.jsx - Navigation sidebar
import { NavLink } from 'react-router-dom'
import { 
  Home, 
  Users, 
  BookOpen, 
  Globe, 
  FileText, 
  Clock, 
  StickyNote,
  LogOut,
  Settings
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'

const Sidebar = () => {
  // const { user, logout } = useAuthStore()
  const user = { username: 'sanskar' } // Mock user for UI testing
  const logout = () => console.log('Logout clicked') // Mock logout function

  const navigation = [
    { name: 'Home', href: '/dashboard', icon: Home, category: 'General' },
    { name: 'Profile', href: '/profile', icon: Users, category: 'General' },
    { name: 'Planner', href: '/planner', icon: BookOpen, category: 'Study Tools' },
    { name: 'Resources', href: '/resources', icon: Globe, category: 'Study Tools' },
    { name: 'Scriba', href: '/scriba', icon: FileText, category: 'Study Tools' },
    { name: 'Timer', href: '/timer', icon: Clock, category: 'Study Tools' },
    { name: 'Notes', href: '/notes', icon: StickyNote, category: 'Study Tools' },
  ]

  const handleLogout = () => {
    logout()
  }

  const groupedNavigation = navigation.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = []
    }
    acc[item.category].push(item)
    return acc
  }, {})

  return (
    <div className="w-64 bg-arcade-beige border-r border-arcade-teal h-screen flex flex-col">
      {/* User Profile Section */}
      <div className="p-6 border-b border-arcade-teal">
        <div className="flex flex-col items-center">
          <div className="w-16 h-16 bg-white border-2 border-arcade-teal rounded-full flex items-center justify-center mb-3">
            <span className="text-2xl font-bold text-arcade-teal lowercase">
              {user?.username?.charAt(0) || 'b'}
            </span>
          </div>
          <p className="text-gray-700 text-sm font-medium">
            Welcome, {user?.username || 'sanskar'}
          </p>
          <div className="mt-2">
            <Settings className="h-4 w-4 text-gray-600" />
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 px-4 py-6">
        {Object.entries(groupedNavigation).map(([category, items]) => (
          <div key={category} className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
              {category}
            </h3>
            <nav className="space-y-1">
              {items.map((item) => {
                const Icon = item.icon
                return (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    className={({ isActive }) =>
                      `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 relative ${
                        isActive
                          ? 'text-arcade-teal bg-white border-l-4 border-arcade-teal'
                          : 'text-gray-600 hover:text-gray-800'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-arcade-teal' : 'text-gray-600'}`} />
                        {item.name}
                        {item.name === 'Home' && (
                          <div className="absolute left-0 top-0 bottom-0 w-1 bg-arcade-teal rounded-r"></div>
                        )}
                      </>
                    )}
                  </NavLink>
                )
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Logout button */}
      <div className="p-4 border-t border-arcade-teal">
        <button
          onClick={handleLogout}
          className="group flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 rounded-md transition-colors duration-200 w-full"
        >
          <LogOut className="mr-3 h-5 w-5 text-gray-600" />
          Log out
        </button>
      </div>
    </div>
  )
}

export default Sidebar

