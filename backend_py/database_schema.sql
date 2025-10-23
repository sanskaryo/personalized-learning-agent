-- Database schema for CodeMentor AI
-- Run this in your Supabase SQL Editor

-- ============================================
-- Study Plans Table
-- ============================================
CREATE TABLE IF NOT EXISTS study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subjects TEXT[] NOT NULL,
    study_hours_per_week INTEGER NOT NULL CHECK (study_hours_per_week >= 1 AND study_hours_per_week <= 50),
    difficulty_level TEXT NOT NULL CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    focus_areas TEXT[] DEFAULT '{}',
    schedule JSONB NOT NULL DEFAULT '[]',
    milestones TEXT[] DEFAULT '{}',
    progress JSONB DEFAULT '{}',
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_study_plans_user_id ON study_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_study_plans_status ON study_plans(status);
CREATE INDEX IF NOT EXISTS idx_study_plans_created_at ON study_plans(created_at DESC);

-- Enable Row Level Security
ALTER TABLE study_plans ENABLE ROW LEVEL SECURITY;

-- RLS Policies for study_plans
CREATE POLICY "Users can view their own study plans"
    ON study_plans FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own study plans"
    ON study_plans FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own study plans"
    ON study_plans FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own study plans"
    ON study_plans FOR DELETE
    USING (auth.uid() = user_id);


-- ============================================
-- Notes Table
-- ============================================
CREATE TABLE IF NOT EXISTS notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    subject TEXT NOT NULL DEFAULT 'General',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_subject ON notes(subject);
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- RLS Policies for notes
CREATE POLICY "Users can view their own notes"
    ON notes FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own notes"
    ON notes FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own notes"
    ON notes FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own notes"
    ON notes FOR DELETE
    USING (auth.uid() = user_id);


-- ============================================
-- Trigger to update updated_at timestamp
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to study_plans
CREATE TRIGGER update_study_plans_updated_at 
    BEFORE UPDATE ON study_plans 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to notes
CREATE TRIGGER update_notes_updated_at 
    BEFORE UPDATE ON notes 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- Optional: Sample Data (for testing)
-- ============================================
-- Uncomment to insert sample data for testing
-- Note: Replace 'YOUR_USER_ID' with an actual user ID from auth.users

/*
INSERT INTO study_plans (user_id, subjects, study_hours_per_week, difficulty_level, focus_areas, schedule, milestones)
VALUES (
    'YOUR_USER_ID',
    ARRAY['DSA', 'OS', 'DBMS'],
    15,
    'intermediate',
    ARRAY['Practice', 'Theory'],
    '[
        {
            "week_number": 1,
            "days": [
                {
                    "day": "Monday",
                    "sessions": [
                        {
                            "time": "9:00-10:30",
                            "subject": "DSA",
                            "topic": "Arrays and Strings",
                            "activities": ["Theory", "Practice"],
                            "duration_minutes": 90,
                            "completed": false
                        }
                    ]
                }
            ]
        }
    ]'::jsonb,
    ARRAY['Week 1: Complete basics', 'Week 2: Intermediate topics']
);

INSERT INTO notes (user_id, title, content, subject, tags)
VALUES (
    'YOUR_USER_ID',
    'Introduction to Data Structures',
    'Arrays are contiguous memory locations that store elements of the same type...',
    'DSA',
    ARRAY['arrays', 'basics', 'data-structures']
);
*/
