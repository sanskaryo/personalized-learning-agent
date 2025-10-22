// src/pages/Dashboard.jsx - Main dashboard page
import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import api from '../utils/api'

const Dashboard = () => {
  // const { user } = useAuthStore()
  const user = { username: 'sanskar' } // Mock user for UI testing
  const [stats, setStats] = useState({
    totalStudyTime: 0,
    totalSessions: 0,
    totalQuestions: 0,
    subjectsStudied: 0,
    weeklyActivity: []
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // const statsResponse = await api.get('/progress/stats')
      // setStats(statsResponse.data)
      console.log('API call commented out for UI testing')
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Generate calendar grid data (13 months)
  const generateCalendarData = () => {
    const months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    
    // Create a grid of empty squares (all showing no activity)
    const grid = []
    for (let week = 0; week < 7; week++) {
      const weekRow = []
      for (let month = 0; month < 13; month++) {
        weekRow.push({ activity: 0 }) // 0 = no activity (lightest color)
      }
      grid.push(weekRow)
    }
    
    return { months, days, grid }
  }

  const calendarData = generateCalendarData()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-arcade-teal"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <h1 className="text-3xl font-bold text-arcade-teal">
          {user?.username || 'sanskar'}'s Study Activity
        </h1>
        <p className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleDateString('en-GB')}
        </p>
      </div>

      {/* Study Contributions Section */}
      <div className="bg-white rounded-lg border border-arcade-teal p-6">
        <h2 className="text-xl font-bold text-arcade-teal mb-6">Your Study Contributions</h2>
        
        {/* Calendar Grid */}
        <div className="mb-4">
          {/* Month headers */}
          <div className="flex mb-2">
            <div className="w-12"></div> {/* Empty space for day labels */}
            {calendarData.months.map((month, index) => (
              <div key={index} className="w-8 text-center text-sm text-gray-600">
                {month}
              </div>
            ))}
          </div>
          
          {/* Calendar grid */}
          {calendarData.days.map((day, weekIndex) => (
            <div key={weekIndex} className="flex mb-1">
              <div className="w-12 text-sm text-gray-600 pr-2">
                {day}
              </div>
              {calendarData.grid[weekIndex].map((cell, monthIndex) => (
                <div
                  key={`${weekIndex}-${monthIndex}`}
                  className={`w-6 h-6 mx-0.5 rounded-sm ${
                    cell.activity === 0 ? 'bg-gray-100' :
                    cell.activity === 1 ? 'bg-green-200' :
                    cell.activity === 2 ? 'bg-green-300' :
                    cell.activity === 3 ? 'bg-green-400' : 'bg-arcade-teal'
                  }`}
                ></div>
              ))}
            </div>
          ))}
        </div>
        
        {/* Legend */}
        <div className="flex items-center justify-end space-x-2 text-sm">
          <span className="text-gray-600">Less</span>
          <div className="flex space-x-1">
            <div className="w-3 h-3 bg-gray-100 rounded-sm"></div>
            <div className="w-3 h-3 bg-green-200 rounded-sm"></div>
            <div className="w-3 h-3 bg-green-300 rounded-sm"></div>
            <div className="w-3 h-3 bg-green-400 rounded-sm"></div>
            <div className="w-3 h-3 bg-arcade-teal rounded-sm"></div>
          </div>
          <span className="text-gray-600">More</span>
        </div>
        
        {/* Bottom border */}
        <div className="mt-6 h-1 bg-arcade-teal rounded"></div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-arcade-teal p-6 text-center">
          <h3 className="text-sm text-gray-600 mb-2">Current Streak</h3>
          <p className="text-2xl font-bold text-arcade-teal">0 days</p>
        </div>
        <div className="bg-white rounded-lg border border-arcade-teal p-6 text-center">
          <h3 className="text-sm text-gray-600 mb-2">Total Study Days</h3>
          <p className="text-2xl font-bold text-arcade-teal">0 days</p>
        </div>
        <div className="bg-white rounded-lg border border-arcade-teal p-6 text-center">
          <h3 className="text-sm text-gray-600 mb-2">Best Streak</h3>
          <p className="text-2xl font-bold text-arcade-teal">0 days</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

