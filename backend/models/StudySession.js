// models/StudySession.js - Track study sessions and progress
import mongoose from 'mongoose';

const studySessionSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  subject: {
    type: String,
    required: true,
    enum: ['DSA', 'OS', 'DBMS', 'CN', 'SE', 'AI', 'ML', 'Web Dev', 'Mobile Dev']
  },
  topic: {
    type: String,
    required: true
  },
  duration: {
    type: Number, // in minutes
    required: true,
    min: 1
  },
  difficulty: {
    type: String,
    enum: ['easy', 'medium', 'hard'],
    default: 'medium'
  },
  questionsAsked: {
    type: Number,
    default: 0
  },
  conceptsLearned: [String],
  notes: String,
  rating: {
    type: Number,
    min: 1,
    max: 5
  },
  completed: {
    type: Boolean,
    default: true
  },
  startTime: {
    type: Date,
    default: Date.now
  },
  endTime: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Index for efficient queries
studySessionSchema.index({ userId: 1, subject: 1, createdAt: -1 });

export default mongoose.model('StudySession', studySessionSchema);

