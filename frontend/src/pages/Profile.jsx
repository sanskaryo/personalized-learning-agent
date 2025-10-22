// src/pages/Profile.jsx - User profile page
import { useState, useEffect } from 'react'
import { User, Save, Edit3, BookOpen, Target } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

const Profile = () => {
  const { user, updateProfile } = useAuthStore()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    year: user?.year || '2nd',
    subjects: user?.subjects || [],
    learningStyle: user?.learningStyle || 'visual',
    studyGoals: user?.studyGoals || []
  })
  const [newGoal, setNewGoal] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const subjects = ['DSA', 'OS', 'DBMS', 'CN', 'SE', 'AI', 'ML', 'Web Dev', 'Mobile Dev']
  const years = ['1st', '2nd', '3rd', '4th']
  const learningStyles = [
    { value: 'visual', label: 'Visual' },
    { value: 'auditory', label: 'Auditory' },
    { value: 'kinesthetic', label: 'Hands-on' },
    { value: 'reading', label: 'Reading/Writing' }
  ]

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubjectChange = (subject) => {
    setFormData({
      ...formData,
      subjects: formData.subjects.includes(subject)
        ? formData.subjects.filter(s => s !== subject)
        : [...formData.subjects, subject]
    })
  }

  const addGoal = () => {
    if (newGoal.trim() && !formData.studyGoals.includes(newGoal.trim())) {
      setFormData({
        ...formData,
        studyGoals: [...formData.studyGoals, newGoal.trim()]
      })
      setNewGoal('')
    }
  }

  const removeGoal = (goalToRemove) => {
    setFormData({
      ...formData,
      studyGoals: formData.studyGoals.filter(goal => goal !== goalToRemove)
    })
  }

  const handleSave = async () => {
    setIsLoading(true)
    
    const result = await updateProfile(formData)
    
    if (result.success) {
      toast.success('Profile updated successfully!')
      setIsEditing(false)
    } else {
      toast.error(result.error || 'Failed to update profile')
    }
    
    setIsLoading(false)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
          <p className="text-gray-600">Manage your account and learning preferences</p>
        </div>
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="btn-secondary flex items-center space-x-2"
        >
          <Edit3 className="h-4 w-4" />
          <span>{isEditing ? 'Cancel' : 'Edit Profile'}</span>
        </button>
      </div>

      {/* Profile info */}
      <div className="card">
        <div className="flex items-center space-x-6 mb-6">
          <div className="h-20 w-20 rounded-full bg-primary-100 flex items-center justify-center">
            <span className="text-2xl font-bold text-primary-600">
              {user?.username?.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{user?.username}</h2>
            <p className="text-gray-600">{user?.email}</p>
            <p className="text-sm text-gray-500">{user?.year} Year CSE Student</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Academic Year */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Academic Year
            </label>
            {isEditing ? (
              <select
                name="year"
                value={formData.year}
                onChange={handleChange}
                className="input-field"
              >
                {years.map(year => (
                  <option key={year} value={year}>{year} Year</option>
                ))}
              </select>
            ) : (
              <p className="text-gray-900">{user?.year} Year</p>
            )}
          </div>

          {/* Learning Style */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Learning Style
            </label>
            {isEditing ? (
              <select
                name="learningStyle"
                value={formData.learningStyle}
                onChange={handleChange}
                className="input-field"
              >
                {learningStyles.map(style => (
                  <option key={style.value} value={style.value}>{style.label}</option>
                ))}
              </select>
            ) : (
              <p className="text-gray-900">
                {learningStyles.find(s => s.value === user?.learningStyle)?.label}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Subjects */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <BookOpen className="h-5 w-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">Subjects of Interest</h3>
        </div>
        
        {isEditing ? (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {subjects.map(subject => (
              <label key={subject} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.subjects.includes(subject)}
                  onChange={() => handleSubjectChange(subject)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-3 text-sm text-gray-700">{subject}</span>
              </label>
            ))}
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {user?.subjects?.length > 0 ? (
              user.subjects.map(subject => (
                <span
                  key={subject}
                  className="px-3 py-1 bg-primary-100 text-primary-800 text-sm rounded-full"
                >
                  {subject}
                </span>
              ))
            ) : (
              <p className="text-gray-500">No subjects selected</p>
            )}
          </div>
        )}
      </div>

      {/* Study Goals */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Target className="h-5 w-5 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">Study Goals</h3>
        </div>
        
        {isEditing ? (
          <div className="space-y-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                placeholder="Add a new study goal..."
                className="flex-1 input-field"
                onKeyPress={(e) => e.key === 'Enter' && addGoal()}
              />
              <button
                onClick={addGoal}
                className="btn-primary"
              >
                Add
              </button>
            </div>
            <div className="space-y-2">
              {formData.studyGoals.map((goal, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-900">{goal}</span>
                  <button
                    onClick={() => removeGoal(goal)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {user?.studyGoals?.length > 0 ? (
              user.studyGoals.map((goal, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-900">{goal}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No study goals set</p>
            )}
          </div>
        )}
      </div>

      {/* Save button */}
      {isEditing && (
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={isLoading}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            <span>{isLoading ? 'Saving...' : 'Save Changes'}</span>
          </button>
        </div>
      )}
    </div>
  )
}

export default Profile

