// src/pages/Timer.jsx - Study Session Timer
import { useState, useEffect, useRef } from 'react'
import { Play, Pause, Square, Clock, BookOpen } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'

const Timer = () => {
  const [isRunning, setIsRunning] = useState(false)
  const [time, setTime] = useState(0) // in seconds
  const [selectedSubject, setSelectedSubject] = useState('General')
  const [sessionId, setSessionId] = useState(null)
  const [sessionStartTime, setSessionStartTime] = useState(null)
  const intervalRef = useRef(null)

  const subjects = ['General', 'DSA', 'OS', 'DBMS', 'CN', 'SE', 'AI', 'ML', 'Web Dev', 'Mobile Dev']

  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        setTime(prev => prev + 1)
      }, 1000)
    } else {
      clearInterval(intervalRef.current)
    }

    return () => clearInterval(intervalRef.current)
  }, [isRunning])

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const startSession = async () => {
    try {
      const response = await api.post('/api/progress/session/start', {
        subject: selectedSubject
      })
      
      setSessionId(response.data.session_id)
      setSessionStartTime(new Date())
      setIsRunning(true)
      toast.success('Study session started!')
    } catch (error) {
      console.error('Error starting session:', error)
      toast.error('Failed to start session')
    }
  }

  const pauseSession = () => {
    setIsRunning(false)
    toast.info('Session paused')
  }

  const resumeSession = () => {
    setIsRunning(true)
    toast.info('Session resumed')
  }

  const endSession = async () => {
    if (!sessionId) return

    try {
      await api.put(`/api/progress/session/${sessionId}/end`)
      
      setIsRunning(false)
      setSessionId(null)
      setSessionStartTime(null)
      setTime(0)
      toast.success(`Session completed! Duration: ${formatTime(time)}`)
    } catch (error) {
      console.error('Error ending session:', error)
      toast.error('Failed to end session')
    }
  }

  const resetTimer = () => {
    setIsRunning(false)
    setTime(0)
    setSessionId(null)
    setSessionStartTime(null)
  }

  return (
    <div className="max-w-2xl mx-auto p-8 bg-arcade-beige min-h-screen">
      <div className="bg-white rounded-lg border border-arcade-teal p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-arcade-teal mb-2">Study Timer</h1>
          <p className="text-gray-600">Track your focused study sessions</p>
        </div>

        {/* Subject Selection */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Subject
          </label>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            disabled={isRunning}
            className="w-full px-4 py-2 border border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal disabled:bg-gray-100"
          >
            {subjects.map(subject => (
              <option key={subject} value={subject}>{subject}</option>
            ))}
          </select>
        </div>

        {/* Timer Display */}
        <div className="text-center mb-8">
          <div className="text-6xl font-mono font-bold text-arcade-teal mb-4">
            {formatTime(time)}
          </div>
          <div className="flex items-center justify-center space-x-2 text-gray-600">
            <BookOpen className="h-4 w-4" />
            <span>{selectedSubject}</span>
            {sessionStartTime && (
              <>
                <span>•</span>
                <Clock className="h-4 w-4" />
                <span>Started: {sessionStartTime.toLocaleTimeString()}</span>
              </>
            )}
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex justify-center space-x-4 mb-8">
          {!isRunning && !sessionId ? (
            <button
              onClick={startSession}
              className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <Play className="h-5 w-5" />
              <span>Start Session</span>
            </button>
          ) : (
            <>
              {isRunning ? (
                <button
                  onClick={pauseSession}
                  className="bg-yellow-500 hover:bg-yellow-600 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 flex items-center space-x-2"
                >
                  <Pause className="h-5 w-5" />
                  <span>Pause</span>
                </button>
              ) : (
                <button
                  onClick={resumeSession}
                  className="bg-green-500 hover:bg-green-600 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 flex items-center space-x-2"
                >
                  <Play className="h-5 w-5" />
                  <span>Resume</span>
                </button>
              )}
              
              <button
                onClick={endSession}
                className="bg-red-500 hover:bg-red-600 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 flex items-center space-x-2"
              >
                <Square className="h-5 w-5" />
                <span>End Session</span>
              </button>
            </>
          )}
        </div>

        {/* Session Info */}
        {sessionId && (
          <div className="bg-arcade-teal-light border border-arcade-teal rounded-lg p-4">
            <h3 className="font-semibold text-arcade-teal mb-2">Active Session</h3>
            <div className="text-sm text-gray-700 space-y-1">
              <p><strong>Session ID:</strong> {sessionId.slice(-8)}</p>
              <p><strong>Subject:</strong> {selectedSubject}</p>
              <p><strong>Status:</strong> {isRunning ? 'Running' : 'Paused'}</p>
              {sessionStartTime && (
                <p><strong>Started:</strong> {sessionStartTime.toLocaleString()}</p>
              )}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="mt-8 text-center">
          <button
            onClick={resetTimer}
            disabled={isRunning}
            className="text-gray-500 hover:text-gray-700 text-sm disabled:opacity-50"
          >
            Reset Timer
          </button>
        </div>
      </div>
    </div>
  )
}

export default Timer
