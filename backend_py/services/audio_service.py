"""
Audio Transcription Service using AssemblyAI
Handles audio file transcription with chapter detection
"""

import os
from typing import Dict, List, Optional
import assemblyai as aai
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AudioTranscriptionService:
    """Service for transcribing audio files using AssemblyAI"""
    
    def __init__(self):
        """Initialize AssemblyAI client"""
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key:
            logger.warning("ASSEMBLYAI_API_KEY not found in environment variables")
            self.client = None
        else:
            aai.settings.api_key = api_key
            self.client = aai.Transcriber()
            logger.info("AudioTranscriptionService initialized successfully")
    
    async def transcribe_audio(
        self, 
        audio_file_path: str,
        enable_chapters: bool = True
    ) -> Dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file or URL
            enable_chapters: Whether to enable automatic chapter detection
            
        Returns:
            Dictionary containing transcription results
        """
        if not self.client:
            logger.error("AssemblyAI client not initialized - missing API key")
            raise ValueError("AssemblyAI service is not configured. Please add ASSEMBLYAI_API_KEY to environment variables.")
        
        try:
            logger.info(f"Starting transcription for file: {audio_file_path}")
            
            # Configure transcription
            config = aai.TranscriptionConfig(
                auto_chapters=enable_chapters,
                speaker_labels=False
            )
            
            # Transcribe
            transcript = self.client.transcribe(audio_file_path, config=config)
            
            if transcript.status == aai.TranscriptStatus.error:
                logger.error(f"Transcription failed: {transcript.error}")
                raise Exception(f"Transcription failed: {transcript.error}")
            
            logger.info(f"Transcription completed successfully. Text length: {len(transcript.text)} characters")
            
            result = {
                "text": transcript.text,
                "confidence": transcript.confidence if hasattr(transcript, 'confidence') else None,
                "duration": transcript.audio_duration if hasattr(transcript, 'audio_duration') else None,
                "word_count": len(transcript.text.split()),
                "chapters": None
            }
            
            # Extract chapters if available
            if enable_chapters and hasattr(transcript, 'chapters') and transcript.chapters:
                result["chapters"] = [
                    {
                        "gist": chapter.gist,
                        "headline": chapter.headline,
                        "summary": chapter.summary,
                        "start": chapter.start,
                        "end": chapter.end
                    }
                    for chapter in transcript.chapters
                ]
                logger.info(f"Extracted {len(result['chapters'])} chapters from audio")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}", exc_info=True)
            raise
    
    async def transcribe_with_timestamps(
        self, 
        audio_file_path: str
    ) -> Dict:
        """
        Transcribe audio with word-level timestamps
        
        Args:
            audio_file_path: Path to audio file or URL
            
        Returns:
            Dictionary with text and word timestamps
        """
        if not self.client:
            raise ValueError("AssemblyAI service is not configured")
        
        try:
            logger.info(f"Starting transcription with timestamps: {audio_file_path}")
            
            transcript = self.client.transcribe(audio_file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                logger.error(f"Transcription failed: {transcript.error}")
                raise Exception(f"Transcription failed: {transcript.error}")
            
            words_with_timestamps = []
            if hasattr(transcript, 'words') and transcript.words:
                words_with_timestamps = [
                    {
                        "text": word.text,
                        "start": word.start,
                        "end": word.end,
                        "confidence": word.confidence
                    }
                    for word in transcript.words
                ]
            
            logger.info(f"Transcription with timestamps completed. Words: {len(words_with_timestamps)}")
            
            return {
                "text": transcript.text,
                "words": words_with_timestamps,
                "duration": transcript.audio_duration if hasattr(transcript, 'audio_duration') else None
            }
            
        except Exception as e:
            logger.error(f"Error during timestamped transcription: {str(e)}", exc_info=True)
            raise
    
    def check_service_health(self) -> bool:
        """Check if the service is properly configured"""
        return self.client is not None
