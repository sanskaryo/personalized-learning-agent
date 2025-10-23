"""
Flashcard Generation Service using Gemini AI
Generates flashcards from notes and content with spaced repetition
"""

import json
from typing import List, Dict
from .gemini import GeminiService
from ..utils.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)


class FlashcardService:
    """Service for generating and managing flashcards"""
    
    def __init__(self):
        """Initialize Gemini service for flashcard generation"""
        self.gemini = GeminiService()
        logger.info("FlashcardService initialized successfully")
    
    async def generate_flashcards(
        self, 
        content: str, 
        count: int = 5,
        difficulty: str = "medium"
    ) -> List[Dict]:
        """
        Generate flashcards from content using AI
        
        Args:
            content: Text content to generate flashcards from
            count: Number of flashcards to generate
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            List of generated flashcards
        """
        try:
            logger.info(f"Generating {count} flashcards with {difficulty} difficulty")
            
            prompt = f"""Generate {count} high-quality flashcards from the following content.
            Difficulty level: {difficulty}
            
            Requirements:
            - Create clear, specific questions that test understanding
            - Provide concise, accurate answers
            - Include helpful hints where appropriate
            - Vary question types (definition, application, comparison, etc.)
            - Ensure questions are self-contained and unambiguous
            
            Format the output as a JSON array with this exact structure:
            [
                {{
                    "question": "Clear, specific question text",
                    "answer": "Concise, accurate answer",
                    "difficulty": "{difficulty}",
                    "hint": "Optional helpful hint (can be null)"
                }}
            ]
            
            Content to generate flashcards from:
            {content}
            
            Return ONLY the JSON array, no additional text or markdown formatting."""
            
            response = await self.gemini.generate_content(prompt)
            
            # Clean and parse JSON response
            json_text = response.strip()
            
            # Remove markdown code blocks if present
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            json_text = json_text.strip()
            
            # Parse JSON
            flashcards = json.loads(json_text)
            
            # Validate structure
            if not isinstance(flashcards, list):
                logger.error("Generated flashcards is not a list")
                raise ValueError("Invalid flashcard format returned by AI")
            
            # Ensure all required fields
            validated_flashcards = []
            for idx, card in enumerate(flashcards):
                if "question" in card and "answer" in card:
                    validated_flashcards.append({
                        "question": card["question"],
                        "answer": card["answer"],
                        "difficulty": card.get("difficulty", difficulty),
                        "hint": card.get("hint")
                    })
                else:
                    logger.warning(f"Skipping invalid flashcard at index {idx}")
            
            logger.info(f"Successfully generated {len(validated_flashcards)} flashcards")
            return validated_flashcards
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Raw response: {response}")
            
            # Fallback: Try to extract questions from content
            return self._fallback_extraction(content, count, difficulty)
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}", exc_info=True)
            raise
    
    def _fallback_extraction(
        self, 
        content: str, 
        count: int, 
        difficulty: str
    ) -> List[Dict]:
        """
        Fallback method to extract flashcards when AI parsing fails
        Uses simple pattern matching to create basic flashcards
        """
        logger.info("Using fallback extraction method")
        
        flashcards = []
        sentences = content.split('.')
        
        for sentence in sentences[:count]:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Look for definition patterns
            if ' is ' in sentence.lower() or ' are ' in sentence.lower():
                parts = sentence.split(' is ' if ' is ' in sentence else ' are ', 1)
                if len(parts) == 2:
                    flashcards.append({
                        "question": f"What is {parts[0].strip()}?",
                        "answer": parts[1].strip(),
                        "difficulty": difficulty,
                        "hint": None
                    })
            
            if len(flashcards) >= count:
                break
        
        logger.info(f"Fallback extraction created {len(flashcards)} flashcards")
        return flashcards
    
    def calculate_next_review(
        self, 
        performance: str,
        current_interval: int = 1
    ) -> Dict:
        """
        Calculate next review date using spaced repetition (SM-2 algorithm)
        
        Args:
            performance: User's performance rating (again, hard, good, easy)
            current_interval: Current interval in days
            
        Returns:
            Dictionary with next review date and interval
        """
        # SuperMemo SM-2 algorithm intervals
        intervals = {
            "again": 1,      # Review again tomorrow
            "hard": max(1, int(current_interval * 1.2)),    # Slight increase
            "good": max(1, int(current_interval * 2.5)),    # Standard increase
            "easy": max(1, int(current_interval * 3.0))     # Large increase
        }
        
        next_interval = intervals.get(performance, 1)
        next_review_date = datetime.now() + timedelta(days=next_interval)
        
        logger.debug(f"Calculated next review: {next_interval} days (performance: {performance})")
        
        return {
            "next_interval_days": next_interval,
            "next_review_date": next_review_date.isoformat(),
            "performance": performance
        }
    
    async def generate_from_note(
        self, 
        note_content: str,
        note_title: str,
        count: int = 5
    ) -> List[Dict]:
        """
        Generate flashcards specifically formatted for a note
        
        Args:
            note_content: Content of the note
            note_title: Title of the note for context
            count: Number of flashcards to generate
            
        Returns:
            List of flashcards
        """
        logger.info(f"Generating flashcards from note: {note_title}")
        
        enhanced_content = f"""Note Title: {note_title}
        
Content:
{note_content}"""
        
        return await self.generate_flashcards(enhanced_content, count)
