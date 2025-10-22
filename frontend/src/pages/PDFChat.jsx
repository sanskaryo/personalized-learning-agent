// src/pages/PDFChat.jsx - Interactive PDF Chat Assistant
import { useState, useRef } from 'react'
import { Upload, MessageSquare, FileText, ZoomIn, ZoomOut, RotateCw, Maximize, X } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'

const PDFChat = () => {
  const [uploadedFile, setUploadedFile] = useState(null)
  const [messages, setMessages] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [pdfInfo, setPdfInfo] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [zoom, setZoom] = useState(100)
  const [rotation, setRotation] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (file.type !== 'application/pdf') {
      toast.error('Please upload a PDF file')
      return
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast.error('File size too large. Maximum 10MB allowed.')
      return
    }

    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post('/api/pdf/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setUploadedFile(response.data)
      setPdfInfo(response.data)
      setMessages([])
      toast.success('PDF uploaded and processed successfully!')
    } catch (error) {
      console.error('Error uploading PDF:', error)
      toast.error('Failed to upload PDF')
    } finally {
      setIsUploading(false)
    }
  }

  const askQuestion = async () => {
    if (!currentQuestion.trim() || !uploadedFile) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: currentQuestion,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setCurrentQuestion('')
    setIsLoading(true)

    try {
      const response = await api.post('/api/pdf/chat', {
        file_id: uploadedFile.file_id,
        question: currentQuestion
      })

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        relevantPages: response.data.relevant_pages,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error asking question:', error)
      toast.error('Failed to process question')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      askQuestion()
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="max-w-7xl mx-auto p-8 bg-arcade-beige min-h-screen">
      <div className="bg-white rounded-lg border border-arcade-teal p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-arcade-teal mb-2">Interactive PDF Chat Assistant</h1>
          <p className="text-gray-600">Upload a PDF and chat with it using AI</p>
        </div>

        {!uploadedFile ? (
          /* Upload Section */
          <div className="text-center py-12">
            <div className="border-2 border-dashed border-arcade-teal rounded-lg p-12">
              <Upload className="h-16 w-16 text-arcade-teal mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-arcade-teal mb-2">Upload PDF Document</h3>
              <p className="text-gray-600 mb-6">Upload a PDF file to start chatting with it</p>
              
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
              />
              
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 disabled:opacity-50"
              >
                {isUploading ? 'Processing...' : 'Choose PDF File'}
              </button>
              
              <p className="text-sm text-gray-500 mt-4">Maximum file size: 10MB</p>
            </div>
          </div>
        ) : (
          /* Chat Interface */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* PDF Info and Controls */}
            <div className="space-y-6">
              <div className="bg-arcade-teal-light border border-arcade-teal rounded-lg p-6">
                <h3 className="text-lg font-semibold text-arcade-teal mb-4">Document Info</h3>
                <div className="space-y-2">
                  <p><strong>File:</strong> {pdfInfo.filename}</p>
                  <p><strong>Pages:</strong> {pdfInfo.total_pages}</p>
                  <p><strong>Status:</strong> <span className="text-green-600">Ready for chat</span></p>
                </div>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Document Summary</h3>
                <p className="text-gray-600">{pdfInfo.document_summary}</p>
              </div>

              {/* PDF Controls */}
              <div className="bg-white border border-arcade-teal rounded-lg p-6">
                <h3 className="text-lg font-semibold text-arcade-teal mb-4">PDF Controls</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Page</label>
                    <input
                      type="number"
                      min="1"
                      max={pdfInfo.total_pages}
                      value={currentPage}
                      onChange={(e) => setCurrentPage(parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Zoom</label>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setZoom(Math.max(50, zoom - 25))}
                        className="p-2 border border-arcade-teal rounded-lg hover:bg-gray-50"
                      >
                        <ZoomOut className="h-4 w-4" />
                      </button>
                      <span className="text-sm font-medium">{zoom}%</span>
                      <button
                        onClick={() => setZoom(Math.min(200, zoom + 25))}
                        className="p-2 border border-arcade-teal rounded-lg hover:bg-gray-50"
                      >
                        <ZoomIn className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
                
                <div className="mt-4 flex items-center space-x-4">
                  <button
                    onClick={() => setRotation((rotation + 90) % 360)}
                    className="p-2 border border-arcade-teal rounded-lg hover:bg-gray-50"
                  >
                    <RotateCw className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setIsFullscreen(!isFullscreen)}
                    className="p-2 border border-arcade-teal rounded-lg hover:bg-gray-50"
                  >
                    <Maximize className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Chat Section */}
            <div className="space-y-6">
              {/* Messages */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 h-96 overflow-y-auto">
                {messages.length === 0 ? (
                  <div className="text-center py-8">
                    <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Start a conversation</h3>
                    <p className="text-gray-600">Ask questions about the PDF document</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.role === 'user'
                            ? 'bg-arcade-teal text-white'
                            : 'bg-white border border-arcade-teal text-gray-800'
                        }`}>
                          <p className="text-sm">{message.content}</p>
                          {message.relevantPages && message.relevantPages.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-gray-200">
                              <p className="text-xs text-gray-600 mb-1">Relevant pages:</p>
                              <div className="flex flex-wrap gap-1">
                                {message.relevantPages.map((page, index) => (
                                  <span
                                    key={index}
                                    className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                                  >
                                    Page {page.page_number}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                    
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-white border border-arcade-teal rounded-lg px-4 py-2">
                          <div className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-arcade-teal"></div>
                            <span className="text-sm text-gray-600">AI is thinking...</span>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="space-y-4">
                <textarea
                  value={currentQuestion}
                  onChange={(e) => setCurrentQuestion(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a question about the PDF..."
                  className="w-full px-4 py-3 border border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal resize-none"
                  rows="3"
                  disabled={isLoading}
                />
                
                <div className="flex justify-between items-center">
                  <button
                    onClick={() => {
                      setUploadedFile(null)
                      setMessages([])
                      setPdfInfo(null)
                    }}
                    className="text-gray-500 hover:text-gray-700 text-sm"
                  >
                    Upload New PDF
                  </button>
                  
                  <button
                    onClick={askQuestion}
                    disabled={!currentQuestion.trim() || isLoading}
                    className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50"
                  >
                    Ask Question
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PDFChat
