import { useState, useEffect } from 'react'
import { Plus, Save, Trash2, Edit3, BookOpen, Search } from 'lucide-react'
import api from '../utils/api'
import toast from 'react-hot-toast'

const Notes = () => {
  const [notes, setNotes] = useState([])
  const [selectedNote, setSelectedNote] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSubject, setSelectedSubject] = useState('All')
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    subject: 'General',
    tags: []
  })

  const subjects = ['All', 'General', 'DSA', 'OS', 'DBMS', 'CN', 'SE', 'AI', 'ML', 'Web Dev', 'Mobile Dev']

  useEffect(() => {
    fetchNotes()
  }, [])

  const fetchNotes = async () => {
    try {
      const response = await api.get('/api/notes')
      setNotes(response.data)
    } catch (error) {
      console.error('Error fetching notes:', error)
      toast.error('Failed to load notes')
    }
  }

  const createNote = async () => {
    if (!formData.title.trim() || !formData.content.trim()) {
      toast.error('Please fill in all fields')
      return
    }

    try {
      const response = await api.post('/api/notes', formData)
      setNotes([response.data, ...notes])
      resetForm()
      toast.success('Note created successfully!')
    } catch (error) {
      console.error('Error creating note:', error)
      toast.error('Failed to create note')
    }
  }

  const updateNote = async () => {
    if (!selectedNote) return

    try {
      const response = await api.put(`/api/notes/${selectedNote.id}`, formData)
      setNotes(notes.map(n => n.id === selectedNote.id ? response.data : n))
      setIsEditing(false)
      setSelectedNote(response.data)
      toast.success('Note updated successfully!')
    } catch (error) {
      console.error('Error updating note:', error)
      toast.error('Failed to update note')
    }
  }

  const deleteNote = async (noteId) => {
    if (!window.confirm('Are you sure you want to delete this note?')) return

    try {
      await api.delete(`/api/notes/${noteId}`)
      setNotes(notes.filter(n => n.id !== noteId))
      if (selectedNote?.id === noteId) {
        setSelectedNote(null)
      }
      toast.success('Note deleted successfully!')
    } catch (error) {
      console.error('Error deleting note:', error)
      toast.error('Failed to delete note')
    }
  }

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      subject: 'General',
      tags: []
    })
    setIsEditing(false)
    setSelectedNote(null)
  }

  const editNote = (note) => {
    setFormData({
      title: note.title,
      content: note.content,
      subject: note.subject,
      tags: note.tags || []
    })
    setSelectedNote(note)
    setIsEditing(true)
  }

  const filteredNotes = notes.filter(note => {
    const matchesSearch = note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         note.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesSubject = selectedSubject === 'All' || note.subject === selectedSubject
    return matchesSearch && matchesSubject
  })

  return (
    <div className="max-w-7xl mx-auto p-8 bg-arcade-beige min-h-screen">
      <div className="bg-white rounded-lg border-4 border-arcade-teal p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-arcade-teal mb-2">My Notes</h1>
            <p className="text-gray-600">Organize your study notes and insights</p>
          </div>
          <button
            onClick={() => {
              resetForm()
              setIsEditing(true)
            }}
            className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
          >
            <Plus className="h-5 w-5" />
            <span>New Note</span>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar with note list */}
          <div className="lg:col-span-1 space-y-4">
            {/* Search and Filter */}
            <div className="space-y-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search notes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border-2 border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
                />
              </div>

              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="w-full px-3 py-2 border-2 border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
              >
                {subjects.map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>

            {/* Notes List */}
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {filteredNotes.map(note => (
                <div
                  key={note.id}
                  onClick={() => {
                    setSelectedNote(note)
                    setIsEditing(false)
                  }}
                  className={`p-4 rounded-lg cursor-pointer transition-colors ${
                    selectedNote?.id === note.id
                      ? 'bg-arcade-teal text-white'
                      : 'bg-arcade-beige hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold line-clamp-1">{note.title}</h3>
                    <BookOpen className="h-4 w-4" />
                  </div>
                  <p className={`text-sm line-clamp-2 ${
                    selectedNote?.id === note.id ? 'text-white/90' : 'text-gray-600'
                  }`}>
                    {note.content}
                  </p>
                  <div className="flex items-center justify-between mt-2">
                    <span className={`text-xs ${
                      selectedNote?.id === note.id ? 'text-white/75' : 'text-gray-500'
                    }`}>
                      {note.subject}
                    </span>
                    <span className={`text-xs ${
                      selectedNote?.id === note.id ? 'text-white/75' : 'text-gray-500'
                    }`}>
                      {new Date(note.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}

              {filteredNotes.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No notes found
                </div>
              )}
            </div>
          </div>

          {/* Note Editor/Viewer */}
          <div className="lg:col-span-2">
            {isEditing ? (
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Note Title"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-4 py-2 text-xl font-semibold border-2 border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
                />

                <select
                  value={formData.subject}
                  onChange={(e) => setFormData({...formData, subject: e.target.value})}
                  className="px-3 py-2 border-2 border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal"
                >
                  {subjects.filter(s => s !== 'All').map(subject => (
                    <option key={subject} value={subject}>{subject}</option>
                  ))}
                </select>

                <textarea
                  placeholder="Start writing your note..."
                  value={formData.content}
                  onChange={(e) => setFormData({...formData, content: e.target.value})}
                  rows={20}
                  className="w-full px-4 py-3 border-2 border-arcade-teal rounded-lg focus:outline-none focus:ring-2 focus:ring-arcade-teal resize-none"
                />

                <div className="flex items-center space-x-3">
                  <button
                    onClick={selectedNote ? updateNote : createNote}
                    className="bg-arcade-teal hover:bg-arcade-teal-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
                  >
                    <Save className="h-5 w-5" />
                    <span>{selectedNote ? 'Update' : 'Save'} Note</span>
                  </button>
                  <button
                    onClick={resetForm}
                    className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors duration-200"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : selectedNote ? (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-arcade-teal">{selectedNote.title}</h2>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => editNote(selectedNote)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <Edit3 className="h-5 w-5 text-gray-600" />
                    </button>
                    <button
                      onClick={() => deleteNote(selectedNote.id)}
                      className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="h-5 w-5 text-red-600" />
                    </button>
                  </div>
                </div>

                <div className="mb-4">
                  <span className="px-3 py-1 bg-arcade-beige text-arcade-teal rounded-full text-sm font-medium">
                    {selectedNote.subject}
                  </span>
                  <span className="ml-3 text-sm text-gray-500">
                    {new Date(selectedNote.created_at).toLocaleDateString()}
                  </span>
                </div>

                <div className="prose max-w-none">
                  <p className="whitespace-pre-wrap text-gray-700">{selectedNote.content}</p>
                </div>
              </div>
            ) : (
              <div className="text-center py-16 text-gray-500">
                <BookOpen className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                <p>Select a note to view or create a new one</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Notes
