// src/pages/Progress.jsx - Progress tracking page
import { useState, useEffect } from 'react'
import { BarChart3, Clock, BookOpen, TrendingUp, Calendar } from 'lucide-react'
import api from '../utils/api'

const Progress = () => {
  const [stats, setStats] = useState({
    totalStudyTime: 0,
    totalSessions: 0,
    totalQuestions: 0,
    subjectsStudied: 0,
    subjectStats: [],
    weeklyActivity: []
  })
  const [selectedPeriod, setSelectedPeriod] = useState('30d')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchProgressData()
  }, [selectedPeriod])

  const fetchProgressData = async () => {
    try {
      const response = await api.get(`/progress/stats?period=${selectedPeriod}`)
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching progress data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const periods = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' }
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Progress Tracking</h1>
          <p className="text-gray-600">Monitor your learning journey and achievements</p>
        </div>
        <div className="flex items-center space-x-2">
          <Calendar className="h-5 w-5 text-gray-400" />
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {periods.map(period => (
              <option key={period.value} value={period.value}>{period.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Overview stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-100 mr-4">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Study Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.round(stats.totalStudyTime / 60)}h
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-green-100 mr-4">
              <BookOpen className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Study Sessions</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalSessions}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-purple-100 mr-4">
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Questions Asked</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalQuestions}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-orange-100 mr-4">
              <TrendingUp className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Subjects Studied</p>
              <p className="text-2xl font-bold text-gray-900">{stats.subjectsStudied}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Subject breakdown */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Subject Breakdown</h3>
        <div className="space-y-4">
          {stats.subjectStats.length > 0 ? (
            stats.subjectStats.map((subject, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{subject.subject}</h4>
                  <p className="text-sm text-gray-600">
                    {subject.sessions} sessions • {Math.round(subject.totalTime / 60)}h
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {subject.questions} questions
                  </p>
                  <p className="text-xs text-gray-500">
                    Avg rating: {subject.averageRating.toFixed(1)}/5
                  </p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-8">No subject data available</p>
          )}
        </div>
      </div>

      {/* Weekly activity */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Activity</h3>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
          <p className="text-gray-500">Activity chart coming soon...</p>
        </div>
      </div>
    </div>
  )
}

export default Progress

