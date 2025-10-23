-- ============================================
-- Phase 1: Database Schema Updates
-- Audio Transcription, OCR, PYQ, Flashcards, Gamification
-- ============================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. Audio Transcriptions Table
-- ============================================
CREATE TABLE IF NOT EXISTS audio_transcriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subject VARCHAR(255) DEFAULT 'General',
    topic VARCHAR(255) DEFAULT 'Lecture Notes',
    original_filename TEXT,
    transcription_text TEXT NOT NULL,
    confidence FLOAT,
    duration_seconds INTEGER,
    chapters JSONB,
    word_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_audio_transcriptions_user_id ON audio_transcriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_audio_transcriptions_created_at ON audio_transcriptions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audio_transcriptions_subject ON audio_transcriptions(subject);

-- Enable RLS
ALTER TABLE audio_transcriptions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own transcriptions"
    ON audio_transcriptions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own transcriptions"
    ON audio_transcriptions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own transcriptions"
    ON audio_transcriptions FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own transcriptions"
    ON audio_transcriptions FOR DELETE
    USING (auth.uid() = user_id);


-- ============================================
-- 2. OCR Extractions Table
-- ============================================
CREATE TABLE IF NOT EXISTS ocr_extractions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    extracted_text TEXT NOT NULL,
    image_url TEXT,
    subject VARCHAR(255) DEFAULT 'General',
    topic VARCHAR(255) DEFAULT 'Handwritten Notes',
    confidence FLOAT,
    word_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ocr_extractions_user_id ON ocr_extractions(user_id);
CREATE INDEX IF NOT EXISTS idx_ocr_extractions_created_at ON ocr_extractions(created_at DESC);

-- Enable RLS
ALTER TABLE ocr_extractions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own OCR extractions"
    ON ocr_extractions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own OCR extractions"
    ON ocr_extractions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own OCR extractions"
    ON ocr_extractions FOR DELETE
    USING (auth.uid() = user_id);


-- ============================================
-- 3. PYQ Questions Table
-- ============================================
CREATE TABLE IF NOT EXISTS pyq_questions (
    id VARCHAR(255) PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    question_text TEXT NOT NULL,
    marks INTEGER DEFAULT 10,
    difficulty VARCHAR(50) DEFAULT 'medium',
    year INTEGER DEFAULT 2024,
    key_points JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pyq_questions_user_id ON pyq_questions(user_id);
CREATE INDEX IF NOT EXISTS idx_pyq_questions_subject ON pyq_questions(subject);
CREATE INDEX IF NOT EXISTS idx_pyq_questions_difficulty ON pyq_questions(difficulty);

-- Enable RLS
ALTER TABLE pyq_questions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own PYQ questions"
    ON pyq_questions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own PYQ questions"
    ON pyq_questions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own PYQ questions"
    ON pyq_questions FOR UPDATE
    USING (auth.uid() = user_id);


-- ============================================
-- 4. PYQ Submissions Table
-- ============================================
CREATE TABLE IF NOT EXISTS pyq_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question_id VARCHAR(255) NOT NULL,
    question_text TEXT NOT NULL,
    answer TEXT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    score FLOAT DEFAULT 0,
    max_score FLOAT DEFAULT 10,
    evaluation JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pyq_submissions_user_id ON pyq_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_pyq_submissions_question_id ON pyq_submissions(question_id);
CREATE INDEX IF NOT EXISTS idx_pyq_submissions_subject ON pyq_submissions(subject);
CREATE INDEX IF NOT EXISTS idx_pyq_submissions_created_at ON pyq_submissions(created_at DESC);

-- Enable RLS
ALTER TABLE pyq_submissions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own PYQ submissions"
    ON pyq_submissions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own PYQ submissions"
    ON pyq_submissions FOR INSERT
    WITH CHECK (auth.uid() = user_id);


-- ============================================
-- 5. Flashcards Table
-- ============================================
CREATE TABLE IF NOT EXISTS flashcards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    difficulty VARCHAR(50) DEFAULT 'medium',
    hint TEXT,
    source TEXT,  -- 'note:note_id' or 'direct_content'
    note_id UUID REFERENCES notes(id) ON DELETE SET NULL,
    next_review_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    review_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_flashcards_user_id ON flashcards(user_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_next_review_date ON flashcards(next_review_date);
CREATE INDEX IF NOT EXISTS idx_flashcards_note_id ON flashcards(note_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_difficulty ON flashcards(difficulty);

-- Enable RLS
ALTER TABLE flashcards ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own flashcards"
    ON flashcards FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own flashcards"
    ON flashcards FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own flashcards"
    ON flashcards FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own flashcards"
    ON flashcards FOR DELETE
    USING (auth.uid() = user_id);


-- ============================================
-- 6. User Points Table (Gamification)
-- ============================================
CREATE TABLE IF NOT EXISTS user_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    points INTEGER DEFAULT 0,
    action_type VARCHAR(100),  -- 'note_created', 'quiz_completed', 'streak_maintained', etc.
    reference_id TEXT,  -- Reference to the action (note_id, quiz_id, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_points_user_id ON user_points(user_id);
CREATE INDEX IF NOT EXISTS idx_user_points_action_type ON user_points(action_type);
CREATE INDEX IF NOT EXISTS idx_user_points_created_at ON user_points(created_at DESC);

-- Enable RLS
ALTER TABLE user_points ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own points"
    ON user_points FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own points"
    ON user_points FOR INSERT
    WITH CHECK (auth.uid() = user_id);


-- ============================================
-- 7. User Achievements Table (Gamification)
-- ============================================
CREATE TABLE IF NOT EXISTS user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    achievement_type VARCHAR(100) UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url TEXT,
    rarity VARCHAR(50) DEFAULT 'common',  -- common, uncommon, rare, epic, legendary
    unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_unlocked_at ON user_achievements(unlocked_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_achievements_rarity ON user_achievements(rarity);

-- Enable RLS
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own achievements"
    ON user_achievements FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own achievements"
    ON user_achievements FOR INSERT
    WITH CHECK (auth.uid() = user_id);


-- ============================================
-- 8. Study Sessions Table (for streak tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS study_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    duration_seconds INTEGER DEFAULT 0,
    activity_type VARCHAR(50),  -- 'note_reading', 'quiz', 'flashcard_review', 'pyq_practice'
    subject VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_study_sessions_user_id ON study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_created_at ON study_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_study_sessions_activity_type ON study_sessions(activity_type);

-- Enable RLS
ALTER TABLE study_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own study sessions"
    ON study_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own study sessions"
    ON study_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);


-- ============================================
-- 9. Update existing notes table (if needed)
-- Add tags column if it doesn't exist
-- ============================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='notes' AND column_name='tags') THEN
        ALTER TABLE notes ADD COLUMN tags TEXT[] DEFAULT ARRAY[]::TEXT[];
    END IF;
END $$;


-- ============================================
-- 10. Create useful views
-- ============================================

-- User statistics view
CREATE OR REPLACE VIEW user_stats_view AS
SELECT 
    u.id as user_id,
    u.email,
    COALESCE(SUM(up.points), 0) as total_points,
    COUNT(DISTINCT n.id) as total_notes,
    COUNT(DISTINCT f.id) as total_flashcards,
    COUNT(DISTINCT ps.id) as total_pyq_submissions,
    COUNT(DISTINCT ua.id) as total_achievements
FROM auth.users u
LEFT JOIN user_points up ON u.id = up.user_id
LEFT JOIN notes n ON u.id = n.user_id
LEFT JOIN flashcards f ON u.id = f.user_id
LEFT JOIN pyq_submissions ps ON u.id = ps.user_id
LEFT JOIN user_achievements ua ON u.id = ua.user_id
GROUP BY u.id, u.email;


-- ============================================
-- Success message
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✅ Phase 1 database migration completed successfully!';
    RAISE NOTICE '📊 Created tables:';
    RAISE NOTICE '   - audio_transcriptions';
    RAISE NOTICE '   - ocr_extractions';
    RAISE NOTICE '   - pyq_questions';
    RAISE NOTICE '   - pyq_submissions';
    RAISE NOTICE '   - flashcards';
    RAISE NOTICE '   - user_points';
    RAISE NOTICE '   - user_achievements';
    RAISE NOTICE '   - study_sessions';
    RAISE NOTICE '🔒 All tables have RLS enabled';
    RAISE NOTICE '📈 Created user_stats_view for analytics';
END $$;
