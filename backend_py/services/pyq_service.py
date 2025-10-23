"""
PYQ (Previous Year Questions) Service using Gemini AI
Generates exam-style questions and evaluates student answers
"""

import json
from typing import List, Dict
from .gemini import GeminiService
from ..utils.logger import get_logger
import uuid

logger = get_logger(__name__)


class PYQService:
    """Service for generating and evaluating Previous Year Questions"""
    
    def __init__(self):
        """Initialize Gemini service"""
        self.gemini = GeminiService()
        logger.info("PYQService initialized successfully")
    
    async def generate_questions(
        self,
        subject: str,
        topic: str,
        difficulty: str = "medium",
        count: int = 10
    ) -> List[Dict]:
        """
        Generate Previous Year Question style questions
        
        Args:
            subject: Subject name
            topic: Topic within the subject
            difficulty: Question difficulty (easy, medium, hard)
            count: Number of questions to generate
            
        Returns:
            List of generated questions
        """
        try:
            logger.info(f"Generating {count} {difficulty} PYQs for {subject} - {topic}")
            
            prompt = f"""Generate {count} previous year examination style questions for {subject} on topic: {topic}.
            
Difficulty level: {difficulty}

Requirements:
- Create university/competitive exam level questions
- Include a mix of short answer (2-3 marks) and long answer (5-10 marks) questions
- Questions should test conceptual understanding and application
- Include key points that should be covered in the answer
- Make questions challenging and exam-oriented
- Vary question types (explain, compare, analyze, solve, derive, etc.)

Format as JSON array with this exact structure:
[
    {{
        "id": "q1",
        "question": "Detailed question text",
        "marks": 5,
        "topic": "{topic}",
        "year": 2024,
        "difficulty": "{difficulty}",
        "key_points": ["Key point 1 to cover", "Key point 2 to cover", "Key point 3 to cover"]
    }}
]

Make questions realistic and exam-worthy. Return ONLY the JSON array."""
            
            response = await self.gemini.generate_content(prompt)
            
            # Clean and parse JSON
            json_text = response.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()
            
            questions = json.loads(json_text)
            
            # Validate and add unique IDs
            validated_questions = []
            for idx, q in enumerate(questions):
                if "question" in q and "marks" in q:
                    q["id"] = q.get("id", f"q{idx+1}_{uuid.uuid4().hex[:8]}")
                    q["topic"] = q.get("topic", topic)
                    q["difficulty"] = q.get("difficulty", difficulty)
                    q["year"] = q.get("year", 2024)
                    q["key_points"] = q.get("key_points", [])
                    validated_questions.append(q)
            
            logger.info(f"Successfully generated {len(validated_questions)} questions")
            return validated_questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Failed to generate questions. Please try again.")
            
        except Exception as e:
            logger.error(f"Error generating PYQ questions: {str(e)}", exc_info=True)
            raise
    
    async def evaluate_answer(
        self,
        question_text: str,
        student_answer: str,
        subject: str,
        max_marks: int = 10
    ) -> Dict:
        """
        Evaluate student's answer using AI
        
        Args:
            question_text: The question asked
            student_answer: Student's answer
            subject: Subject context
            max_marks: Maximum marks for the question
            
        Returns:
            Evaluation with score and feedback
        """
        try:
            logger.info(f"Evaluating answer for question in {subject}")
            
            prompt = f"""Evaluate this student answer for an examination question.

Subject: {subject}
Max Marks: {max_marks}

Question:
{question_text}

Student Answer:
{student_answer}

Provide a comprehensive evaluation as JSON with this exact structure:
{{
    "score": 8.5,
    "max_score": {max_marks},
    "feedback": "Overall constructive feedback on the answer quality and completeness",
    "strengths": ["Strength 1: specific positive aspect", "Strength 2: another good point"],
    "improvements": ["Improvement 1: specific area to improve", "Improvement 2: another suggestion"],
    "missing_concepts": ["Concept 1 that should have been mentioned", "Concept 2 not covered"],
    "exam_tips": ["Tip 1: specific exam technique", "Tip 2: writing strategy"]
}}

Be fair but constructive in evaluation. Consider:
- Correctness and accuracy
- Completeness of answer
- Clarity of explanation
- Proper use of terminology
- Logical structure

Return ONLY the JSON object."""
            
            response = await self.gemini.generate_content(prompt)
            
            # Clean and parse JSON
            json_text = response.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()
            
            evaluation = json.loads(json_text)
            
            # Validate structure
            required_fields = ["score", "max_score", "feedback", "strengths", "improvements"]
            for field in required_fields:
                if field not in evaluation:
                    logger.warning(f"Missing field in evaluation: {field}")
                    evaluation[field] = [] if field in ["strengths", "improvements", "missing_concepts", "exam_tips"] else ""
            
            # Ensure score is within range
            evaluation["score"] = min(max(0, evaluation["score"]), evaluation["max_score"])
            
            logger.info(f"Evaluation completed. Score: {evaluation['score']}/{evaluation['max_score']}")
            return evaluation
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation JSON: {str(e)}")
            raise ValueError("Failed to evaluate answer. Please try again.")
            
        except Exception as e:
            logger.error(f"Error evaluating answer: {str(e)}", exc_info=True)
            raise
    
    async def get_question_hints(
        self,
        question_text: str,
        subject: str
    ) -> List[str]:
        """
        Generate helpful hints for a question
        
        Args:
            question_text: The question
            subject: Subject context
            
        Returns:
            List of hints
        """
        try:
            logger.info(f"Generating hints for question in {subject}")
            
            prompt = f"""Generate 3 helpful hints for solving this exam question.
            
Subject: {subject}
Question: {question_text}

Hints should:
- Not give away the answer directly
- Guide thinking process
- Point to relevant concepts
- Be progressively more helpful

Return as JSON array: ["Hint 1", "Hint 2", "Hint 3"]"""
            
            response = await self.gemini.generate_content(prompt)
            
            json_text = response.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            hints = json.loads(json_text.strip())
            
            logger.info(f"Generated {len(hints)} hints")
            return hints if isinstance(hints, list) else []
            
        except Exception as e:
            logger.error(f"Error generating hints: {str(e)}")
            return ["Think about the core concepts", "Break down the problem", "Review your notes on this topic"]
