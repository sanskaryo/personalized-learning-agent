# ExamPrepAgent Analysis & Implementation Plan

## 🎯 Repository Overview
**URL**: https://github.com/cardea-mcp/ExamPrepAgent

ExamPrepAgent is an AI-powered exam preparation assistant that uses:
- **MCP (Model Context Protocol)** servers for tool integration
- **TiDB** database with full-text search capabilities
- **LLM integration** for intelligent Q&A interactions
- **FastAPI** backend with clean architecture
- **Voice features** (ASR/TTS) for accessibility

---

## 🌟 Key Features We Can Learn From

### 1. **MCP Server Architecture** ⭐⭐⭐
**What it is**: Model Context Protocol allows LLMs to use external tools/functions

**Their Implementation**:
```python
# main.py - MCP Server
from fastmcp import FastMCP

mcp = FastMCP("Exam-Bot")

@mcp.tool()
def get_random_question(topic: Optional[str] = None):
    """Get random practice question from database"""
    result = get_random_qa(topic)
    return result

# Runs as separate server on port 9096
mcp.run(transport="http", host="127.0.0.1", port=9096, path="/mcp")
```

**Why it's powerful**:
- LLM can intelligently decide WHEN to call tools
- Decoupled architecture - MCP server separate from main app
- Enables complex workflows (get question → evaluate answer → explain)

---

### 2. **Q&A Dataset Generation Pipeline** ⭐⭐⭐⭐
**Most Impressive Feature!**

**Their 3-Step Process**:

#### Step 1: Web Scraping (`dataset/dataPrep.py`)
```python
class URLScraper:
    def scrape_url(self, url: str):
        # Scrapes educational content from URLs
        # Cleans HTML, extracts main content
        # Returns structured data
```

#### Step 2: AI-Powered Q&A Generation
```python
class OpenAIQAGenerator:
    def generate_qa_pairs(self, content_data):
        # Uses GPT-4 to generate:
        # - Multiple choice questions
        # - Practical command questions
        # - Detailed explanations
        # Returns JSON with question/answer/explanation
```

#### Step 3: CSV Storage & Database Loading
```python
class CSVWriter:
    def write_to_csv(qa_pairs, filename):
        # Appends to CSV file
        # Format: question, answer, explanation

# Then loads to TiDB database with full-text search index
```

**Example Generated Q&A**:
```json
{
  "question": "What is the default restart policy for a Pod?",
  "answer": "Always",
  "explanation": "The default restart policy is 'Always', meaning containers restart whenever they exit..."
}
```

---

### 3. **TiDB Full-Text Search Integration** ⭐⭐⭐
**Smart Database Usage**:

```python
# database/tidb.py
class TiDBConnection:
    def search_pair(self, query_text: str):
        """Full-text search for relevant Q&A"""
        search_sql = """
        SELECT question, answer, 
               fts_match_word(%s, content) as _score
        FROM qa_table 
        WHERE fts_match_word(%s, content)
        ORDER BY _score DESC 
        LIMIT 3
        """
        return results
    
    def get_random_qa(self, topic: Optional[str] = None):
        """Get random question, optionally filtered by topic"""
        if topic:
            # Full-text search for topic
            # Return random from top 3 matches
        else:
            # Return completely random question
```

**Key Benefits**:
- Semantic search for relevant questions
- Topic-based filtering
- Random selection for variety

---

### 4. **Session Management System** ⭐⭐⭐
**Local Storage Based**:

```javascript
// static/script.js
class ExamBotApp {
    STORAGE_KEYS = {
        USER: 'exambot_user',
        SESSIONS: 'exambot_sessions',
        CURRENT_SESSION: 'exambot_current_session',
        SESSION_PREFIX: 'exambot_session_'
    }
    
    createNewSession(sessionName = null) {
        const session = {
            id: generateSessionId(),
            name: sessionName || `Study Session ${date}`,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            messageCount: 0
        };
        this.sessions.push(session);
        this.saveSessions();
    }
    
    buildConversationContext() {
        // Returns last 20 messages for context
        const messages = this.getSessionMessages(this.currentSession);
        return messages.slice(-20);
    }
}
```

**Features**:
- Multiple study sessions per user
- Persistent across browser reloads
- Maintains conversation context
- Session naming and editing

---

### 5. **Audio Transcription Integration** ⭐⭐
**Voice Input Support**:

```python
# app.py
@app.post("/api/chat/audio")
async def process_chat_audio(
    audio_file: UploadFile,
    context: str = None,
    language: Optional[str] = None
):
    # Validate audio file
    is_valid = validate_audio_file(contents, filename)
    
    # Create temp file for processing
    temp_file = create_temp_audio_file(contents, filename)
    
    # Transcribe using Whisper
    transcription = whisper_handler.transcribe(temp_file)
    
    # Process as chat message with context
    response = process_message_with_context(transcription, context)
    
    return {"transcription": transcription, "response": response}
```

---

### 6. **Clean API Architecture** ⭐⭐⭐
**Well-Organized Backend**:

```
backend_py/
├── routers/           # API endpoints
│   ├── chat.py
│   ├── progress.py
│   ├── pyq.py
│   ├── flashcards.py
│   └── gamification.py
├── services/          # Business logic
│   ├── gemini.py
│   ├── pyq_service.py
│   └── flashcard_service.py
├── dependencies/      # Auth & middleware
│   └── auth.py
├── utils/            # Helpers
│   ├── logger.py
│   └── supabase_client.py
└── schemas.py        # Pydantic models
```

---

## 💡 What We Should Implement

### **Priority 1: Q&A Dataset Generation System** 🔥

**Create New Files**:

1. **`backend_py/services/dataset_generator.py`**
```python
from typing import Dict, List
import json

class DatasetGenerator:
    """Generate Q&A pairs from educational content"""
    
    def __init__(self, gemini_service):
        self.gemini = gemini_service
    
    async def scrape_content(self, url: str) -> Dict:
        """Scrape educational content from URL"""
        # Use BeautifulSoup to extract content
        # Clean and format text
        return {
            'url': url,
            'title': title,
            'content': cleaned_content,
            'length': len(content)
        }
    
    async def generate_qa_pairs(self, content_data: Dict, count: int = 5) -> List[Dict]:
        """Generate Q&A pairs using AI"""
        prompt = f"""
        Based on this educational content, generate {count} high-quality questions.
        
        Content: {content_data['content']}
        
        Return JSON array:
        [
          {{
            "question": "...",
            "answer": "...",
            "explanation": "...",
            "difficulty": "easy|medium|hard"
          }}
        ]
        """
        
        response = await self.gemini.generate_structured_content(prompt)
        return self._parse_qa_pairs(response)
    
    def _parse_qa_pairs(self, response: Dict) -> List[Dict]:
        """Parse and validate generated Q&A pairs"""
        # Extract JSON, validate structure
        # Return cleaned pairs
        pass
```

2. **`backend_py/routers/dataset.py`**
```python
from fastapi import APIRouter, HTTPException
from ..schemas import DatasetGenerateRequest, DatasetGenerateResponse
from ..services.dataset_generator import DatasetGenerator

router = APIRouter(prefix="/api/dataset", tags=["dataset"])

@router.post("/generate-from-url", response_model=DatasetGenerateResponse)
async def generate_from_url(request: DatasetGenerateRequest):
    """Generate Q&A dataset from educational URL"""
    generator = DatasetGenerator(get_gemini_service())
    
    # Scrape content
    content = await generator.scrape_content(request.url)
    
    # Generate Q&A pairs
    qa_pairs = await generator.generate_qa_pairs(
        content,
        count=request.question_count
    )
    
    # Save to database
    saved_ids = await save_qa_to_database(qa_pairs, request.subject)
    
    return {
        "total_generated": len(qa_pairs),
        "questions": qa_pairs,
        "saved_ids": saved_ids
    }
```

3. **Add to `schemas.py`**:
```python
class DatasetGenerateRequest(BaseModel):
    url: str = Field(..., description="Educational content URL")
    subject: str
    question_count: int = Field(5, ge=1, le=20)
    difficulty: Optional[str] = "mixed"

class DatasetGenerateResponse(BaseModel):
    total_generated: int
    questions: List[Dict[str, Any]]
    saved_ids: List[str]
```

---

### **Priority 2: Enhanced PYQ System with Topic-Based Search** 🔥

**Enhance `backend_py/services/pyq_service.py`**:

```python
class PYQService:
    
    async def get_random_question_by_topic(
        self, 
        subject: str, 
        topic: Optional[str] = None
    ) -> Dict:
        """Get random question, optionally filtered by topic"""
        
        if topic:
            # Full-text search in Supabase
            # Get top 3 relevant questions
            # Return random from those 3
            result = supabase.rpc(
                'search_questions_by_topic',
                {'subject_name': subject, 'search_term': topic}
            ).limit(3).execute()
            
            if result.data:
                return random.choice(result.data)
        
        # Fallback to completely random
        return await self.get_random_question(subject)
    
    async def get_adaptive_question(
        self,
        user_id: str,
        subject: str
    ) -> Dict:
        """Get question based on user's weak areas"""
        
        # Analyze user's past performance
        weak_topics = await self._analyze_weak_topics(user_id, subject)
        
        if weak_topics:
            # Prioritize questions from weak topics
            return await self.get_random_question_by_topic(
                subject,
                topic=weak_topics[0]
            )
        
        return await self.get_random_question(subject)
```

---

### **Priority 3: Session Management Enhancement** 🔥

**Update `frontend/pages/Chat.jsx`**:

```javascript
// Add session management
const [sessions, setSessions] = useState([]);
const [currentSessionId, setCurrentSessionId] = useState(null);

const createNewSession = (name = null) => {
    const session = {
        id: generateId(),
        name: name || `Study Session ${new Date().toLocaleDateString()}`,
        createdAt: new Date().toISOString(),
        messages: []
    };
    
    localStorage.setItem(`session_${session.id}`, JSON.stringify(session));
    setSessions([...sessions, session]);
    setCurrentSessionId(session.id);
};

const loadSession = (sessionId) => {
    const session = JSON.parse(localStorage.getItem(`session_${sessionId}`));
    setCurrentSessionId(sessionId);
    setMessages(session.messages);
};
```

**Add Sidebar Component**:

```javascript
// frontend/components/SessionSidebar.jsx
export default function SessionSidebar({ sessions, onSessionClick, onNewSession }) {
    return (
        <div className="session-sidebar">
            <button onClick={onNewSession} className="new-session-btn">
                + New Study Session
            </button>
            
            <div className="sessions-list">
                {sessions.map(session => (
                    <div 
                        key={session.id}
                        className="session-item"
                        onClick={() => onSessionClick(session.id)}
                    >
                        <h4>{session.name}</h4>
                        <span>{session.messages.length} messages</span>
                        <small>{new Date(session.createdAt).toLocaleDateString()}</small>
                    </div>
                ))}
            </div>
        </div>
    );
}
```

---

### **Priority 4: Database Schema Enhancement**

**Add to Supabase**:

```sql
-- Create full-text search function for questions
CREATE OR REPLACE FUNCTION search_questions_by_topic(
    subject_name TEXT,
    search_term TEXT
)
RETURNS TABLE (
    id UUID,
    question TEXT,
    answer TEXT,
    explanation TEXT,
    relevance_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.question,
        q.answer,
        q.explanation,
        ts_rank(
            to_tsvector('english', q.question || ' ' || q.answer),
            plainto_tsquery('english', search_term)
        ) as relevance_score
    FROM pyq_questions q
    WHERE q.subject = subject_name
      AND to_tsvector('english', q.question || ' ' || q.answer) @@ 
          plainto_tsquery('english', search_term)
    ORDER BY relevance_score DESC;
END;
$$ LANGUAGE plpgsql;

-- Add indexes for better search performance
CREATE INDEX idx_questions_search 
ON pyq_questions 
USING GIN(to_tsvector('english', question || ' ' || answer));

-- Track user's weak topics
CREATE TABLE user_topic_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    average_score DECIMAL(5,2),
    last_attempted TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, subject, topic)
);
```

---

### **Priority 5: AI-Powered Study Features**

**Create `backend_py/services/study_assistant.py`**:

```python
class StudyAssistant:
    """Intelligent study assistance"""
    
    async def generate_study_path(
        self,
        user_id: str,
        subject: str,
        duration_weeks: int
    ) -> Dict:
        """Generate personalized study path"""
        
        # Get user's current knowledge level
        performance = await self._get_user_performance(user_id, subject)
        
        # Identify weak areas
        weak_topics = self._identify_weak_areas(performance)
        
        # Generate AI-powered study plan
        prompt = f"""
        Create a {duration_weeks}-week study plan for {subject}.
        
        Student's weak areas: {weak_topics}
        Current performance: {performance['average_score']}%
        
        Return a structured study plan with:
        - Weekly topics to focus on
        - Daily study goals
        - Practice question targets
        - Review schedule
        """
        
        plan = await self.gemini.generate_structured_content(prompt)
        return plan
    
    async def get_contextual_hint(
        self,
        question: str,
        user_answer: str
    ) -> str:
        """Provide intelligent hints without giving away answer"""
        
        prompt = f"""
        The student is attempting this question:
        {question}
        
        Their answer: {user_answer}
        
        Provide a helpful hint that:
        1. Doesn't reveal the answer
        2. Points them in the right direction
        3. Encourages critical thinking
        """
        
        return await self.gemini.generate_content(prompt)
```

---

## 📂 New File Structure

```
backend_py/
├── services/
│   ├── gemini.py (✅ already exists)
│   ├── dataset_generator.py (🆕 NEW)
│   ├── study_assistant.py (🆕 NEW)
│   └── search_service.py (🆕 NEW)
├── routers/
│   ├── dataset.py (🆕 NEW)
│   └── study.py (🆕 NEW)
└── utils/
    └── web_scraper.py (🆕 NEW)

frontend/
├── components/
│   ├── SessionSidebar.jsx (🆕 NEW)
│   └── DatasetGenerator.jsx (🆕 NEW)
└── pages/
    ├── DatasetManagement.jsx (🆕 NEW)
    └── StudyPath.jsx (🆕 NEW)

database/
└── migrations/
    └── 006_topic_search.sql (🆕 NEW)
```

---

## 🎯 Implementation Phases

### **Phase 1: Foundation (Week 1)**
- [ ] Set up web scraping utility
- [ ] Create dataset generator service
- [ ] Add dataset generation API endpoint
- [ ] Build simple UI for dataset generation

### **Phase 2: Search Enhancement (Week 2)**
- [ ] Add full-text search to Supabase
- [ ] Implement topic-based question filtering
- [ ] Create search service
- [ ] Update PYQ endpoints to use search

### **Phase 3: Session Management (Week 3)**
- [ ] Implement session storage (localStorage + backend sync)
- [ ] Build session sidebar component
- [ ] Add session persistence
- [ ] Create session management UI

### **Phase 4: AI Features (Week 4)**
- [ ] Build study assistant service
- [ ] Implement adaptive question selection
- [ ] Add contextual hints system
- [ ] Create study path generator

---

## 🔧 Key Technologies to Adopt

1. **BeautifulSoup4** - Web scraping
   ```bash
   pip install beautifulsoup4 requests
   ```

2. **FastMCP** (Optional) - If we want MCP server
   ```bash
   pip install fastmcp
   ```

3. **PostgreSQL Full-Text Search** - Already in Supabase!

---

## 💭 Architectural Learnings

### **1. Separation of Concerns**
- MCP server separate from main app
- Services handle business logic
- Routers only handle HTTP
- Utils for shared functionality

### **2. AI-First Features**
- Use AI to generate content (Q&A pairs)
- Use AI for intelligent tutoring (hints, explanations)
- Use AI for personalization (adaptive learning)

### **3. Data Pipeline**
```
Web Content → AI Generation → Structured Data → Database → Search & Retrieval
```

### **4. Progressive Enhancement**
- Start with basic features
- Add AI enhancements layer by layer
- Each layer adds more intelligence

---

## 🎓 Lessons for Our Project

1. **Content Generation is Key**: Don't manually create questions - use AI to generate them from educational content

2. **Smart Search Matters**: Full-text search makes finding relevant questions much better than random selection

3. **Session Persistence**: Users want to continue where they left off - implement proper session management

4. **Modular Architecture**: Their clean separation of services, routers, and utils makes code maintainable

5. **AI as a Tool**: Use AI not just for chat, but for content generation, evaluation, and personalization

---

## 🚀 Quick Wins We Can Implement Today

1. **Enhance Gemini Service** (30 mins)
   - Add `generate_structured_content()` method
   - Add better error handling
   
2. **Add Dataset Generation** (2-3 hours)
   - Create basic web scraper
   - Add Q&A generation endpoint
   
3. **Improve PYQ System** (1-2 hours)
   - Add topic filtering
   - Implement basic search

4. **Session Management** (2 hours)
   - Add localStorage persistence
   - Create session list UI

---

## 📚 Additional Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **FastMCP GitHub**: https://github.com/jlowin/fastmcp
- **TiDB Docs**: https://docs.pingcap.com/tidb/stable
- **BeautifulSoup Docs**: https://www.crummy.com/software/BeautifulSoup/

---

## ✅ Action Items

1. Review this analysis document
2. Decide on which features to implement first
3. Set up development environment for new dependencies
4. Start with Quick Wins
5. Move to phased implementation

**Ready to build something amazing! 🚀**
