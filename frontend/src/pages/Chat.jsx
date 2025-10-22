// src/pages/Chat.jsx - AI Chat interface
import { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, BookOpen, Code, Lightbulb } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'

const Chat = () => {
  // const { user } = useAuthStore()
  const user = { username: 'sanskar' } // Mock user for UI testing
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [selectedSubject, setSelectedSubject] = useState('General')
  const [sessionId] = useState(() => `session_${Date.now()}`)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const subjects = ['General', 'DSA', 'OS', 'DBMS', 'CN', 'SE', 'AI', 'ML', 'Web Dev', 'Mobile Dev']

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const messageToSend = inputMessage
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await api.post('/api/chat/send', {
        message: messageToSend,
        session_id: sessionId,
        subject: selectedSubject
      })

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.reply,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getMessageIcon = (role) => {
    return role === 'user' ? User : Bot
  }

  const getMessageTypeIcon = (content) => {
    if (content.includes('```') || content.includes('function') || content.includes('class')) {
      return Code
    }
    if (content.includes('explain') || content.includes('concept') || content.includes('theory')) {
      return BookOpen
    }
    return Lightbulb
  }

  return (
    <div className="flex flex-col h-full max-h-screen bg-arcade-beige">
      {/* Chat header */}
      <div className="bg-white border-b border-arcade-teal p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-arcade-teal">AI Chat</h1>
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Subject:</label>
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="px-3 py-1 border border-arcade-teal rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-arcade-teal"
              >
                {subjects.map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Session: {sessionId.slice(-8)}
          </div>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-arcade-teal mb-2">
              Welcome to CodeMentor AI!
            </h3>
            <p className="text-gray-600 mb-4">
              I'm here to help you with your CSE studies. Ask me anything about:
            </p>
            <div className="grid grid-cols-2 gap-2 max-w-md mx-auto">
              {subjects.slice(1).map(subject => (
                <button
                  key={subject}
                  onClick={() => setSelectedSubject(subject)}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                    selectedSubject === subject
                      ? 'bg-arcade-teal-light border-arcade-teal text-arcade-teal'
                      : 'bg-white border-arcade-teal text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {subject}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => {
            const Icon = getMessageIcon(message.role)
            const TypeIcon = getMessageTypeIcon(message.content)
            
            return (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-3xl ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                  <div className={`flex items-start space-x-3 ${
                    message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}>
                    <div className={`flex-shrink-0 ${
                      message.role === 'user' 
                        ? 'bg-arcade-teal text-white' 
                        : 'bg-gray-200 text-gray-600'
                    } rounded-full p-2`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className={`flex-1 ${
                      message.role === 'user' ? 'text-right' : 'text-left'
                    }`}>
                      <div className={`inline-block p-4 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-arcade-teal text-white'
                          : 'bg-white border border-arcade-teal'
                      }`}>
                        <div className="flex items-start space-x-2">
                          {message.role === 'assistant' && (
                            <TypeIcon className="h-4 w-4 text-gray-400 mt-1 flex-shrink-0" />
                          )}
                          <div className="flex-1">
                            <div className="whitespace-pre-wrap text-sm">
                              {message.content}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className={`text-xs text-gray-500 mt-1 ${
                        message.role === 'user' ? 'text-right' : 'text-left'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-3xl">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 bg-gray-200 text-gray-600 rounded-full p-2">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="bg-white border border-arcade-teal rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-arcade-teal"></div>
                    <span className="text-sm text-gray-600">AI is thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="bg-white border-t border-arcade-teal p-4">
        <div className="flex items-end space-x-4">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about coding, algorithms, or CS concepts..."
              className="w-full px-4 py-3 border border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal focus:border-transparent resize-none"
              rows="2"
              disabled={isLoading}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}

export default Chat

