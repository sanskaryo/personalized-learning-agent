// models/ChatMessage.js - Store chat history with AI
import mongoose from 'mongoose';

const chatMessageSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  sessionId: {
    type: String,
    required: true
  },
  subject: {
    type: String,
    enum: ['DSA', 'OS', 'DBMS', 'CN', 'SE', 'AI', 'ML', 'Web Dev', 'Mobile Dev', 'General'],
    default: 'General'
  },
  role: {
    type: String,
    enum: ['user', 'assistant'],
    required: true
  },
  content: {
    type: String,
    required: true
  },
  messageType: {
    type: String,
    enum: ['text', 'code', 'question', 'explanation', 'example'],
    default: 'text'
  },
  codeLanguage: {
    type: String,
    enum: ['javascript', 'python', 'java', 'cpp', 'c', 'sql', 'html', 'css']
  },
  attachments: [{
    type: String, // file paths
    filename: String,
    mimetype: String
  }],
  metadata: {
    tokensUsed: Number,
    responseTime: Number,
    difficulty: String,
    topics: [String]
  },
  isHelpful: {
    type: Boolean,
    default: null
  },
  feedback: String
}, {
  timestamps: true
});

// Index for efficient queries
chatMessageSchema.index({ userId: 1, sessionId: 1, createdAt: -1 });
chatMessageSchema.index({ userId: 1, subject: 1 });

export default mongoose.model('ChatMessage', chatMessageSchema);

