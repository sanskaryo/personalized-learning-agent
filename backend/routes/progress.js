// routes/progress.js - Progress tracking and analytics
import express from 'express';
import StudySession from '../models/StudySession.js';
import ChatMessage from '../models/ChatMessage.js';
import { authenticateToken } from '../middleware/auth.js';

const router = express.Router();

// Start a new study session
router.post('/session/start', authenticateToken, async (req, res) => {
  try {
    const { subject, topic, difficulty = 'medium' } = req.body;

    if (!subject || !topic) {
      return res.status(400).json({ 
        message: 'Subject and topic are required' 
      });
    }

    const session = new StudySession({
      userId: req.user._id,
      subject,
      topic,
      difficulty,
      startTime: new Date()
    });

    await session.save();

    res.status(201).json({
      message: 'Study session started',
      session: {
        id: session._id,
        subject: session.subject,
        topic: session.topic,
        difficulty: session.difficulty,
        startTime: session.startTime
      }
    });
  } catch (error) {
    console.error('Start session error:', error);
    res.status(500).json({ 
      message: 'Server error starting session' 
    });
  }
});

// End a study session
router.put('/session/:sessionId/end', authenticateToken, async (req, res) => {
  try {
    const { sessionId } = req.params;
    const { duration, conceptsLearned, notes, rating } = req.body;

    const session = await StudySession.findOneAndUpdate(
      { 
        _id: sessionId, 
        userId: req.user._id 
      },
      {
        duration: duration || 0,
        conceptsLearned: conceptsLearned || [],
        notes,
        rating,
        endTime: new Date(),
        completed: true
      },
      { new: true }
    );

    if (!session) {
      return res.status(404).json({ 
        message: 'Session not found' 
      });
    }

    res.json({
      message: 'Study session completed',
      session
    });
  } catch (error) {
    console.error('End session error:', error);
    res.status(500).json({ 
      message: 'Server error ending session' 
    });
  }
});

// Get study statistics
router.get('/stats', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    // Calculate date range
    const now = new Date();
    let startDate;
    
    switch (period) {
      case '7d':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case '90d':
        startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
        break;
      default:
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }

    // Get study sessions
    const sessions = await StudySession.find({
      userId: req.user._id,
      createdAt: { $gte: startDate }
    });

    // Get chat activity
    const chatMessages = await ChatMessage.find({
      userId: req.user._id,
      createdAt: { $gte: startDate }
    });

    // Calculate statistics
    const totalStudyTime = sessions.reduce((sum, session) => sum + (session.duration || 0), 0);
    const totalQuestions = chatMessages.filter(msg => msg.role === 'user').length;
    const subjectsStudied = [...new Set(sessions.map(s => s.subject))];
    const averageSessionLength = sessions.length > 0 ? totalStudyTime / sessions.length : 0;

    // Subject-wise breakdown
    const subjectStats = subjectsStudied.map(subject => {
      const subjectSessions = sessions.filter(s => s.subject === subject);
      const subjectTime = subjectSessions.reduce((sum, s) => sum + (s.duration || 0), 0);
      const subjectQuestions = chatMessages.filter(msg => msg.subject === subject).length;
      
      return {
        subject,
        sessions: subjectSessions.length,
        totalTime: subjectTime,
        questions: subjectQuestions,
        averageRating: subjectSessions.reduce((sum, s) => sum + (s.rating || 0), 0) / subjectSessions.length || 0
      };
    });

    // Recent activity
    const recentSessions = sessions
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, 5);

    res.json({
      period,
      totalStudyTime,
      totalSessions: sessions.length,
      totalQuestions,
      subjectsStudied: subjectsStudied.length,
      averageSessionLength: Math.round(averageSessionLength),
      subjectStats,
      recentSessions,
      weeklyActivity: getWeeklyActivity(sessions)
    });
  } catch (error) {
    console.error('Stats error:', error);
    res.status(500).json({ 
      message: 'Server error fetching statistics' 
    });
  }
});

// Get learning progress for a specific subject
router.get('/subject/:subject', authenticateToken, async (req, res) => {
  try {
    const { subject } = req.params;
    const { limit = 20 } = req.query;

    const sessions = await StudySession.find({
      userId: req.user._id,
      subject
    })
    .sort({ createdAt: -1 })
    .limit(parseInt(limit));

    const topics = [...new Set(sessions.map(s => s.topic))];
    const totalTime = sessions.reduce((sum, s) => sum + (s.duration || 0), 0);
    const averageRating = sessions.reduce((sum, s) => sum + (s.rating || 0), 0) / sessions.length || 0;

    res.json({
      subject,
      totalSessions: sessions.length,
      totalTime,
      topicsCovered: topics.length,
      averageRating: Math.round(averageRating * 10) / 10,
      sessions,
      topics
    });
  } catch (error) {
    console.error('Subject progress error:', error);
    res.status(500).json({ 
      message: 'Server error fetching subject progress' 
    });
  }
});

// Helper function to get weekly activity
function getWeeklyActivity(sessions) {
  const weeklyData = [];
  const now = new Date();
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
    const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const dayEnd = new Date(dayStart.getTime() + 24 * 60 * 60 * 1000);
    
    const daySessions = sessions.filter(session => {
      const sessionDate = new Date(session.createdAt);
      return sessionDate >= dayStart && sessionDate < dayEnd;
    });
    
    const dayTime = daySessions.reduce((sum, s) => sum + (s.duration || 0), 0);
    
    weeklyData.push({
      date: dayStart.toISOString().split('T')[0],
      sessions: daySessions.length,
      time: dayTime
    });
  }
  
  return weeklyData;
}

export default router;

