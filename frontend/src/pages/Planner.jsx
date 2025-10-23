import { useState, useEffect } from 'react'
import { Calendar, Clock, BookOpen, CheckCircle, Circle, Plus, TrendingUp, Trash2 } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'

const Planner = () => {
  const [plans, setPlans] = useState([])
  const [activePlan, setActivePlan] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    subjects: [],
    study_hours_per_week: 10,
    difficulty_level: 'intermediate',
    focus_areas: []
  })

  const subjects = ['DSA', 'OS', 'DBMS', 'CN', 'SE', 'AI', 'ML', 'Web Dev', 'Mobile Dev']
  const difficultyLevels = ['beginner', 'intermediate', 'advanced']

  useEffect(() => {
    fetchPlans()
  }, [])

  const fetchPlans = async () => {
    try {
      const response = await api.get('/api/planner/plans')
      setPlans(response.data)
      if (response.data.length > 0) {
        setActivePlan(response.data[0])
      }
    } catch (error) {
      console.error('Error fetching plans:', error)
      toast.error('Failed to load study plans')
    }
  }

  const handleSubjectToggle = (subject) => {
    setFormData(prev => ({
      ...prev,
      subjects: prev.subjects.includes(subject)
        ? prev.subjects.filter(s => s !== subject)
        : [...prev.subjects, subject]
    }))
  }

  const generatePlan = async () => {
    if (formData.subjects.length === 0) {
      toast.error('Please select at least one subject')
      return
    }

    setIsLoading(true)
    try {
      const response = await api.post('/api/planner/generate', formData)
      toast.success('Study plan generated successfully!')
      setShowCreateForm(false)
      await fetchPlans()
      setActivePlan(response.data)
    } catch (error) {
      console.error('Error generating plan:', error)
      toast.error('Failed to generate study plan')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleSessionComplete = async (weekIndex, dayIndex, sessionIndex) => {
    if (!activePlan) return

    try {
      const dayNumber = weekIndex * 7 + dayIndex
      await api.put(`/api/planner/plans/${activePlan.id}/progress`, {
        day: dayNumber,
        session_completed: true
      })
      
      toast.success('Progress updated!')
      await fetchPlans()
    } catch (error) {
      console.error('Error updating progress:', error)
      toast.error('Failed to update progress')
    }
  }

  const deletePlan = async (planId) => {
    if (!window.confirm('Are you sure you want to delete this plan?')) return

    try {
      await api.delete(`/api/planner/plans/${planId}`)
      toast.success('Plan deleted successfully!')
      await fetchPlans()
      if (activePlan?.id === planId) {
        setActivePlan(null)
      }
    } catch (error) {
      console.error('Error deleting plan:', error)
      toast.error('Failed to delete plan')
    }
  }

  return (
    <div className="max-w-7xl mx-auto p-8 bg-arcade-beige min-h-screen">
      <div className="bg-white rounded-lg border-4 border-arcade-teal p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-arcade-teal mb-2">Smart Study Planner</h1>
            <p className="text-gray-600">AI-generated personalized study schedules</p>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
          >
            <Plus className="h-5 w-5" />
            <span>New Plan</span>
          </button>
        </div>

        {/* Create Plan Form */}
        {showCreateForm && (
          <div className="mb-8 p-6 bg-arcade-beige rounded-lg border-2 border-arcade-teal">
            <h3 className="text-lg font-semibold text-arcade-teal mb-4">Create New Study Plan</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Subjects
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {subjects.map(subject => (
                    <label key={subject} className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.subjects.includes(subject)}
                        onChange={() => handleSubjectToggle(subject)}
                        className="rounded border-gray-300 text-arcade-teal focus:ring-arcade-teal"
                      />
                      <span className="ml-2">{subject}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Study Hours Per Week: {formData.study_hours_per_week}h
                </label>
                <input
                  type="range"
                  min="5"
                  max="40"
                  value={formData.study_hours_per_week}
                  onChange={(e) => setFormData({...formData, study_hours_per_week: parseInt(e.target.value)})}
                  className="w-full accent-arcade-teal"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty Level
                </label>
                <select
                  value={formData.difficulty_level}
                  onChange={(e) => setFormData({...formData, difficulty_level: e.target.value})}
                  className="w-full px-3 py-2 border-2 border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
                >
                  {difficultyLevels.map(level => (
                    <option key={level} value={level}>
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={generatePlan}
                disabled={isLoading}
                className="w-full bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50"
              >
                {isLoading ? 'Generating...' : 'Generate Study Plan'}
              </button>
            </div>
          </div>
        )}

        {/* Active Plan Display */}
        {activePlan && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">
                Current Plan: {activePlan.subjects?.join(', ') || 'Study Plan'}
              </h2>
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Clock className="h-4 w-4" />
                  <span>{activePlan.study_hours_per_week}h/week</span>
                </div>
                <button
                  onClick={() => deletePlan(activePlan.id)}
                  className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete plan"
                >
                  <Trash2 className="h-5 w-5 text-red-600" />
                </button>
              </div>
            </div>

            {/* Weekly Schedule */}
            {activePlan.schedule?.map((week, weekIndex) => (
              <div key={weekIndex} className="border-2 border-arcade-teal rounded-lg p-6">
                <h3 className="text-lg font-semibold text-arcade-teal mb-4">
                  Week {week.week_number}
                </h3>

                <div className="space-y-4">
                  {week.days?.map((day, dayIndex) => (
                    <div key={dayIndex} className="bg-arcade-beige rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">{day.day}</h4>
                      
                      <div className="space-y-2">
                        {day.sessions?.map((session, sessionIndex) => (
                          <div
                            key={sessionIndex}
                            className="flex items-start space-x-3 p-3 bg-white rounded-lg border border-gray-200"
                          >
                            <button
                              onClick={() => toggleSessionComplete(weekIndex, dayIndex, sessionIndex)}
                              className="mt-1"
                            >
                              {session.completed ? (
                                <CheckCircle className="h-5 w-5 text-green-500" />
                              ) : (
                                <Circle className="h-5 w-5 text-gray-400" />
                              )}
                            </button>
                            
                            <div className="flex-1">
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-medium text-arcade-teal">
                                  {session.subject}
                                </span>
                                <span className="text-sm text-gray-500">
                                  {session.time}
                                </span>
                              </div>
                              <p className="text-sm text-gray-700">{session.topic}</p>
                              <div className="flex flex-wrap gap-1 mt-2">
                                {session.activities?.map((activity, idx) => (
                                  <span
                                    key={idx}
                                    className="text-xs px-2 py-1 bg-arcade-beige text-gray-700 rounded"
                                  >
                                    {activity}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Milestones */}
            {activePlan.milestones && activePlan.milestones.length > 0 && (
              <div className="border-2 border-arcade-teal rounded-lg p-6">
                <h3 className="text-lg font-semibold text-arcade-teal mb-4 flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Milestones
                </h3>
                <ul className="space-y-2">
                  {activePlan.milestones.map((milestone, index) => (
                    <li key={index} className="flex items-center space-x-2 text-gray-700">
                      <CheckCircle className="h-4 w-4 text-arcade-teal" />
                      <span>{milestone}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {!activePlan && plans.length === 0 && !showCreateForm && (
          <div className="text-center py-12">
            <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Study Plans Yet</h3>
            <p className="text-gray-600 mb-4">Create your first AI-generated study plan</p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Create Study Plan
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Planner
