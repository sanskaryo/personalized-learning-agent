from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any


class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1)
    subject: Optional[str] = None
    session_id: Optional[str] = None


class ChatMessage(BaseModel):
    id: str
    user_id: str
    role: str
    content: str
    session_id: Optional[str] = None
    created_at: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    message_id: Optional[str] = None
    session_id: Optional[str] = None


class StartSessionRequest(BaseModel):
    subject: Optional[str] = None


class StartSessionResponse(BaseModel):
    session_id: str


class EndSessionResponse(BaseModel):
    session_id: str
    duration_seconds: int


class ProgressStats(BaseModel):
    total_seconds: int
    subject_breakdown: Dict[str, int]


# Resource Curation Schemas
class ResourceSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    resource_type: Optional[str] = None
    max_results: Optional[int] = Field(10, ge=1, le=50)


class ResourceResponse(BaseModel):
    title: str
    url: str
    content: str
    excerpts: List[str]
    resource_type: str
    difficulty_level: str
    quality_score: float
    relevance_score: float
    domain: str
    last_updated: str


class ResourceList(BaseModel):
    resources: List[ResourceResponse]
    total_count: int
    query: str
    filters: Dict[str, Any]


# PDF Chat Assistant Schemas
class PDFUploadResponse(BaseModel):
    file_id: str
    filename: str
    status: str
    message: str
    document_summary: str
    total_pages: int


class PDFChatRequest(BaseModel):
    file_id: str
    question: str = Field(..., min_length=1)


class PDFChatResponse(BaseModel):
    response: str
    relevant_pages: List[Dict[str, Any]]
    file_id: str
    question: str
    status: str


class PDFInfoResponse(BaseModel):
    file_id: str
    filename: str
    total_pages: int
    document_summary: str
    total_length: int
    status: str


# Study Planner Schemas
class StudyPlanRequest(BaseModel):
    subjects: List[str] = Field(..., min_items=1)
    study_hours_per_week: int = Field(..., ge=1, le=50)
    difficulty_level: str = Field("intermediate")
    focus_areas: Optional[List[str]] = None


class StudyPlanResponse(BaseModel):
    plan_id: str
    schedule: List[Dict[str, Any]]
    total_weeks: int
    subjects: List[str]
    study_hours_per_week: int
    status: str
    milestones: Optional[List[str]] = []


# Spaced Repetition Schemas
class FlashcardCreate(BaseModel):
    front: str = Field(..., min_length=1)
    back: str = Field(..., min_length=1)
    subject: str
    difficulty: str = Field("medium")
    tags: Optional[List[str]] = None


class FlashcardResponse(BaseModel):
    id: str
    front: str
    back: str
    subject: str
    difficulty: str
    tags: List[str]
    created_at: str
    next_review: str
    review_count: int
    success_rate: float


class FlashcardReviewRequest(BaseModel):
    card_id: str
    user_response: str
    difficulty_rating: int = Field(..., ge=1, le=5)


class FlashcardReviewResponse(BaseModel):
    card_id: str
    correct: bool
    next_review_date: str
    success_rate: float
    status: str


# Notes System Schemas
class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    subject: str
    tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    subject: str
    tags: List[str]
    created_at: str
    updated_at: str
    ai_summary: Optional[str] = None


# Mock Interview Schemas
class InterviewQuestionRequest(BaseModel):
    subject: str
    difficulty: str = Field("medium")
    question_type: str = Field("technical")  # technical, behavioral, system_design


class InterviewQuestionResponse(BaseModel):
    question_id: str
    question: str
    question_type: str
    subject: str
    difficulty: str
    hints: List[str]
    expected_answer: str
    status: str


class InterviewAnswerRequest(BaseModel):
    question_id: str
    user_answer: str


class InterviewAnswerResponse(BaseModel):
    question_id: str
    user_answer: str
    ai_feedback: str
    score: float
    improvements: List[str]
    status: str


# Audio Transcription Schemas
class AudioTranscriptionRequest(BaseModel):
    subject: Optional[str] = "General"
    topic: Optional[str] = "Lecture Notes"
    auto_save_as_note: bool = True


class AudioTranscriptionResponse(BaseModel):
    transcription_id: str
    text: str
    confidence: Optional[float] = None
    duration: Optional[int] = None
    chapters: Optional[List[Dict[str, Any]]] = None
    word_count: int
    note_id: Optional[str] = None
    status: str
    message: str


# OCR Schemas
class OCRRequest(BaseModel):
    subject: Optional[str] = "General"
    topic: Optional[str] = "Handwritten Notes"
    auto_save_as_note: bool = True


class OCRResponse(BaseModel):
    ocr_id: str
    extracted_text: str
    confidence: Optional[float] = None
    word_count: int
    note_id: Optional[str] = None
    status: str
    message: str


# PYQ (Previous Year Questions) Schemas
class PYQGenerateRequest(BaseModel):
    subject: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)
    difficulty: str = Field("medium", regex="^(easy|medium|hard)$")
    count: int = Field(10, ge=1, le=20)


class PYQQuestion(BaseModel):
    id: str
    question: str
    marks: int
    topic: str
    year: int
    difficulty: str
    key_points: List[str]


class PYQGenerateResponse(BaseModel):
    questions: List[PYQQuestion]
    total_count: int
    subject: str
    topic: str


class PYQAnswerSubmission(BaseModel):
    question_id: str
    question_text: str
    answer: str
    subject: str


class PYQEvaluation(BaseModel):
    score: float
    max_score: float
    feedback: str
    strengths: List[str]
    improvements: List[str]
    missing_concepts: List[str]
    exam_tips: List[str]


class PYQEvaluationResponse(BaseModel):
    evaluation: PYQEvaluation
    submission_id: str
    status: str


# Flashcard Generation from Notes Schemas
class FlashcardGenerateRequest(BaseModel):
    note_id: Optional[str] = None
    content: Optional[str] = None
    count: int = Field(5, ge=1, le=20)
    difficulty: Optional[str] = "medium"


class GeneratedFlashcard(BaseModel):
    question: str
    answer: str
    difficulty: str
    hint: Optional[str] = None


class FlashcardGenerateResponse(BaseModel):
    flashcards: List[GeneratedFlashcard]
    total_count: int
    source: str
    status: str


# Gamification Schemas
class UserStats(BaseModel):
    streak: int
    total_points: int
    level: int
    next_level_points: int
    achievements: List[Dict[str, Any]]
    daily_goal_progress: float
    weekly_study_hours: float


class Achievement(BaseModel):
    id: str
    title: str
    description: str
    icon_url: str
    unlocked_at: str
    rarity: str


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    username: str
    points: int
    level: int
    streak: int
