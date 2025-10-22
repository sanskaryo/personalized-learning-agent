// routes/chat.js - Chat routes with Claude AI integration
import express from 'express';
import Anthropic from '@anthropic-ai/sdk';
import ChatMessage from '../models/ChatMessage.js';
import StudySession from '../models/StudySession.js';
import { authenticateToken } from '../middleware/auth.js';

const router = express.Router();
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Get chat history for a session
router.get('/history/:sessionId', authenticateToken, async (req, res) => {
  try {
    const { sessionId } = req.params;
    const { page = 1, limit = 50 } = req.query;

    const messages = await ChatMessage.find({
      userId: req.user._id,
      sessionId
    })
    .sort({ createdAt: 1 })
    .limit(limit * 1)
    .skip((page - 1) * limit);

    res.json({
      messages,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: messages.length
      }
    });
  } catch (error) {
    console.error('Chat history error:', error);
    res.status(500).json({ 
      message: 'Server error fetching chat history' 
    });
  }
});

// Send message to AI
router.post('/send', authenticateToken, async (req, res) => {
  try {
    const { message, sessionId, subject = 'General', messageType = 'text' } = req.body;

    if (!message || !sessionId) {
      return res.status(400).json({ 
        message: 'Message and sessionId are required' 
      });
    }

    // Save user message
    const userMessage = new ChatMessage({
      userId: req.user._id,
      sessionId,
      subject,
      role: 'user',
      content: message,
      messageType
    });
    await userMessage.save();

    // Get recent chat history for context
    const recentMessages = await ChatMessage.find({
      userId: req.user._id,
      sessionId
    })
    .sort({ createdAt: -1 })
    .limit(10);

    // Prepare context for Claude
    const systemPrompt = getSystemPrompt(subject, req.user);
    const conversationHistory = recentMessages
      .reverse()
      .map(msg => ({
        role: msg.role,
        content: msg.content
      }));

    // Call Claude API
    const startTime = Date.now();
    const response = await anthropic.messages.create({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 1000,
      system: systemPrompt,
      messages: conversationHistory
    });

    const responseTime = Date.now() - startTime;
    const aiResponse = response.content[0].text;

    // Save AI response
    const aiMessage = new ChatMessage({
      userId: req.user._id,
      sessionId,
      subject,
      role: 'assistant',
      content: aiResponse,
      messageType: 'explanation',
      metadata: {
        tokensUsed: response.usage?.output_tokens || 0,
        responseTime,
        difficulty: 'medium',
        topics: extractTopics(aiResponse)
      }
    });
    await aiMessage.save();

    res.json({
      message: aiResponse,
      metadata: {
        tokensUsed: response.usage?.output_tokens || 0,
        responseTime,
        sessionId
      }
    });

  } catch (error) {
    console.error('Chat send error:', error);
    res.status(500).json({ 
      message: 'Server error processing message',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// Provide feedback on AI response
router.post('/feedback', authenticateToken, async (req, res) => {
  try {
    const { messageId, isHelpful, feedback } = req.body;

    if (!messageId) {
      return res.status(400).json({ 
        message: 'Message ID is required' 
      });
    }

    const message = await ChatMessage.findOneAndUpdate(
      { 
        _id: messageId, 
        userId: req.user._id 
      },
      { 
        isHelpful, 
        feedback 
      },
      { new: true }
    );

    if (!message) {
      return res.status(404).json({ 
        message: 'Message not found' 
      });
    }

    res.json({
      message: 'Feedback recorded successfully'
    });
  } catch (error) {
    console.error('Feedback error:', error);
    res.status(500).json({ 
      message: 'Server error recording feedback' 
    });
  }
});

// Helper function to generate system prompt based on subject and user
function getSystemPrompt(subject, user) {
  const basePrompt = `You are CodeMentor AI, a specialized AI study companion for Computer Science Engineering students. You help students learn, understand concepts, debug code, and prepare for exams.

Student Profile:
- Year: ${user.year}
- Subjects: ${user.subjects.join(', ')}
- Learning Style: ${user.learningStyle}

Guidelines:
1. Provide clear, step-by-step explanations
2. Use examples relevant to CSE students
3. Adapt explanations to the student's year level
4. Be encouraging and supportive
5. Ask clarifying questions when needed
6. Provide code examples when relevant
7. Suggest practice problems when appropriate`;

  const subjectSpecificPrompts = {
    'DSA': 'Focus on algorithms, data structures, time/space complexity, and coding implementations.',
    'OS': 'Explain operating system concepts, processes, memory management, and system calls.',
    'DBMS': 'Cover database design, SQL queries, normalization, and transaction management.',
    'CN': 'Focus on networking protocols, layers, routing, and network security.',
    'SE': 'Explain software engineering principles, design patterns, and development methodologies.',
    'AI': 'Cover artificial intelligence concepts, algorithms, and machine learning basics.',
    'ML': 'Focus on machine learning algorithms, data preprocessing, and model evaluation.',
    'Web Dev': 'Explain web technologies, frameworks, and best practices.',
    'Mobile Dev': 'Cover mobile development concepts, platforms, and app design.'
  };

  return basePrompt + '\n\n' + (subjectSpecificPrompts[subject] || '');
}

// Helper function to extract topics from AI response
function extractTopics(text) {
  const commonTopics = [
    'algorithms', 'data structures', 'complexity', 'sorting', 'searching',
    'trees', 'graphs', 'dynamic programming', 'recursion', 'arrays',
    'linked lists', 'stacks', 'queues', 'hash tables', 'binary search'
  ];
  
  return commonTopics.filter(topic => 
    text.toLowerCase().includes(topic)
  );
}

export default router;

