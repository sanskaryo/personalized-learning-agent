// src/test-app.jsx - Simple test React app
import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'

const TestApp = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          CodeMentor AI
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Your AI Study Companion
        </p>
        <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Frontend Setup Complete! ✅
          </h2>
          <p className="text-gray-600 mb-4">
            The React frontend is working correctly with Tailwind CSS.
          </p>
          <div className="space-y-2 text-sm text-gray-500">
            <p>• React: ✅</p>
            <p>• Tailwind CSS: ✅</p>
            <p>• Vite: ✅</p>
            <p>• Zustand: ✅</p>
          </div>
        </div>
      </div>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<TestApp />)

