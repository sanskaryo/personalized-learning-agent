// src/pages/Resources.jsx - Smart Resource Curation
import { useState, useEffect } from 'react'
import { Search, Filter, Star, ExternalLink, BookOpen, Video, FileText, Code, GraduationCap, Globe } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'

const Resources = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSubject, setSelectedSubject] = useState('General')
  const [selectedDifficulty, setSelectedDifficulty] = useState('')
  const [selectedType, setSelectedType] = useState('')
  const [resources, setResources] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [showFilters, setShowFilters] = useState(false)

  const subjects = [
    { id: 'General', name: 'General' },
    { id: 'DSA', name: 'DSA' },
    { id: 'OS', name: 'OS' },
    { id: 'DBMS', name: 'DBMS' },
    { id: 'CN', name: 'CN' },
    { id: 'SE', name: 'SE' },
    { id: 'AI', name: 'AI' },
    { id: 'ML', name: 'ML' },
    { id: 'Web Dev', name: 'Web Dev' },
    { id: 'Mobile Dev', name: 'Mobile Dev' }
  ]

  const difficulties = [
    { id: 'beginner', name: 'Beginner' },
    { id: 'intermediate', name: 'Intermediate' },
    { id: 'advanced', name: 'Advanced' }
  ]

  const resourceTypes = [
    { id: 'video', name: 'Video Tutorials', icon: Video },
    { id: 'course', name: 'Online Courses', icon: GraduationCap },
    { id: 'documentation', name: 'Documentation', icon: FileText },
    { id: 'practice', name: 'Practice Exercises', icon: Code },
    { id: 'paper', name: 'Academic Papers', icon: BookOpen }
  ]

  const getResourceIcon = (type) => {
    const resourceType = resourceTypes.find(t => t.id === type)
    return resourceType ? resourceType.icon : Globe
  }

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800'
      case 'intermediate': return 'bg-yellow-100 text-yellow-800'
      case 'advanced': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const searchResources = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query')
      return
    }

    setIsLoading(true)
    try {
      const response = await api.post('/api/resources/search', {
        query: searchQuery,
        subject: selectedSubject,
        difficulty: selectedDifficulty || undefined,
        resource_type: selectedType || undefined,
        max_results: 20
      })

      setResources(response.data.resources)
      toast.success(`Found ${response.data.resources.length} resources`)
    } catch (error) {
      console.error('Error searching resources:', error)
      toast.error('Failed to search resources')
    } finally {
      setIsLoading(false)
    }
  }

  const getTrendingResources = async () => {
    setIsLoading(true)
    try {
      const response = await api.get('/api/resources/trending', {
        params: {
          subject: selectedSubject,
          limit: 15
        }
      })

      setResources(response.data.resources)
      toast.success(`Found ${response.data.resources.length} trending resources`)
    } catch (error) {
      console.error('Error getting trending resources:', error)
      toast.error('Failed to get trending resources')
    } finally {
      setIsLoading(false)
    }
  }

  const getRecommendedResources = async () => {
    setIsLoading(true)
    try {
      const response = await api.get('/api/resources/recommended', {
        params: {
          subject: selectedSubject,
          difficulty: selectedDifficulty || undefined,
          limit: 15
        }
      })

      setResources(response.data.resources)
      toast.success(`Found ${response.data.resources.length} recommended resources`)
    } catch (error) {
      console.error('Error getting recommended resources:', error)
      toast.error('Failed to get recommended resources')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchResources()
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-8 bg-arcade-beige min-h-screen">
      <div className="bg-white rounded-lg border border-arcade-teal p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-arcade-teal mb-2">Smart Resource Curation</h1>
          <p className="text-gray-600">Discover the best educational resources powered by AI</p>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Search for tutorials, courses, documentation..."
                className="w-full px-4 py-3 border border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
              />
            </div>
            <button
              onClick={searchResources}
              disabled={isLoading}
              className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 disabled:opacity-50 flex items-center space-x-2"
            >
              <Search className="h-5 w-5" />
              <span>Search</span>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-6">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 text-arcade-teal hover:text-arcade-teal-dark"
          >
            <Filter className="h-4 w-4" />
            <span>Filters</span>
          </button>

          {showFilters && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="w-full px-3 py-2 border border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
                >
                  {subjects.map(subject => (
                    <option key={subject.id} value={subject.id}>{subject.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                <select
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="w-full px-3 py-2 border border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
                >
                  <option value="">All Levels</option>
                  {difficulties.map(difficulty => (
                    <option key={difficulty.id} value={difficulty.id}>{difficulty.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Resource Type</label>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full px-3 py-2 border border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
                >
                  <option value="">All Types</option>
                  {resourceTypes.map(type => (
                    <option key={type.id} value={type.id}>{type.name}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="mb-8 flex flex-wrap gap-4">
          <button
            onClick={getTrendingResources}
            disabled={isLoading}
            className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50"
          >
            🔥 Trending
          </button>
          <button
            onClick={getRecommendedResources}
            disabled={isLoading}
            className="bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50"
          >
            ⭐ Recommended
          </button>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-arcade-teal mx-auto"></div>
            <p className="text-gray-600 mt-4">Searching for resources...</p>
          </div>
        )}

        {/* Resources Grid */}
        {!isLoading && resources.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((resource, index) => {
              const ResourceIcon = getResourceIcon(resource.resource_type)
              
              return (
                <div key={index} className="bg-white border border-arcade-teal rounded-lg p-6 hover:shadow-lg transition-shadow duration-200">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <ResourceIcon className="h-5 w-5 text-arcade-teal" />
                      <span className="text-sm font-medium text-gray-600">{resource.resource_type}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span className="text-sm text-gray-600">{resource.quality_score.toFixed(1)}</span>
                    </div>
                  </div>

                  <h3 className="text-lg font-semibold text-arcade-teal mb-2 line-clamp-2">
                    {resource.title}
                  </h3>

                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {resource.content}
                  </p>

                  <div className="flex items-center justify-between mb-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(resource.difficulty_level)}`}>
                      {resource.difficulty_level}
                    </span>
                    <span className="text-xs text-gray-500">{resource.domain}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <a
                      href={resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-arcade-teal hover:text-arcade-teal-dark text-sm font-medium flex items-center space-x-1"
                    >
                      <span>Visit Resource</span>
                      <ExternalLink className="h-4 w-4" />
                    </a>
                    <span className="text-xs text-gray-500">
                      {Math.round(resource.relevance_score * 100)}% relevant
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && resources.length === 0 && (
          <div className="text-center py-12">
            <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No resources found</h3>
            <p className="text-gray-600 mb-4">Try searching for different keywords or adjust your filters</p>
            <button
              onClick={getTrendingResources}
              className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Browse Trending Resources
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Resources
