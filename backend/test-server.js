// test-setup.js - Simple test to verify backend setup
import express from 'express';
import cors from 'cors';

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Test route
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'CodeMentor AI Backend is running!',
    timestamp: new Date().toISOString()
  });
});

// Test auth route
app.post('/api/auth/test', (req, res) => {
  res.json({ 
    message: 'Auth endpoint working',
    data: req.body
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Test server running on port ${PORT}`);
  console.log(`📚 Test endpoint: http://localhost:${PORT}/api/health`);
});

