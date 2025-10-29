# CodeMentor AI - Your AI Study Companion

A personalized AI study companion that adapts to each CSE student's learning style, tracks progress, and provides context-aware assistance across subjects, assignments, and exam prep.

## 🚀 Features

### Phase 1: Core Features ✅
- **AI Chat Interface** - Natural conversation with Claude for doubt solving
- **Subject Context** - Select subject (DSA, OS, DBMS, etc.) for contextual answers
- **Code Helper** - Explain code, debug errors, suggest improvements
- **Study Session Tracker** - Track study time per subject
- **User Authentication** - JWT-based signup/login system
- **Progress Dashboard** - Visualize learning progress and statistics

### Phase 2: Advanced Features (Coming Soon)
- **Code Execution Tool** - Run code snippets in-browser
- **Resource Finder** - Search curated study materials
- **Assignment Helper** - Upload assignment PDFs for structured help
- **Smart Study Planner** - AI-generated personalized study schedules

## 🛠️ Tech Stack

### Backend
- **Node.js** + **Express** - Server framework
- **MongoDB** + **Mongoose** - Database and ODM
- **JWT** - Authentication
- **Claude API** - AI integration
- **MCP SDK** - Model Context Protocol

### Frontend
- **React** + **Vite** - UI framework and build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Navigation
- **Axios** - HTTP client

## 📦 Setup Instructions

### Prerequisites
- Node.js 18+ installed
- MongoDB Atlas account (free tier) or local MongoDB
- Anthropic API key
- Git

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create environment file**
   ```bash
   cp env.example .env
   ```

4. **Configure environment variables**
   Edit `.env` file with your values:
   ```env
   MONGO_URI=mongodb://localhost:27017/codementor-ai
   JWT_SECRET=your-super-secret-jwt-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   PORT=5000
   NODE_ENV=development
   ```

5. **Start the backend server**
   ```bash
   npm run dev
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Chat
- `POST /api/chat/send` - Send message to AI
- `GET /api/chat/history/:sessionId` - Get chat history
- `POST /api/chat/feedback` - Provide feedback on AI response

### Progress
- `POST /api/progress/session/start` - Start study session
- `PUT /api/progress/session/:sessionId/end` - End study session
- `GET /api/progress/stats` - Get progress statistics
- `GET /api/progress/subject/:subject` - Get subject-specific progress

## 🎯 Usage

1. **Register/Login** - Create an account or sign in
2. **Set Profile** - Choose your year, subjects, and learning style
3. **Start Chatting** - Ask questions about CS topics
4. **Track Progress** - Monitor your learning journey
5. **Study Sessions** - Start focused study sessions

## 🚀 Deployment

### Backend (Railway)
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Deploy automatically on push to main branch

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🎓 Educational Benefits

- **Reduces learning anxiety** - Private, judgment-free environment
- **Improves retention** - Active recall through conversation
- **Saves time** - Instant answers vs hours of searching
- **Builds confidence** - Step-by-step explanations
- **Exam preparation** - Practice questions and mock tests

---

**Happy Learning! 🎉**

