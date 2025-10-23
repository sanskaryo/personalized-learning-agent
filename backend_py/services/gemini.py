import os
import json
import google.generativeai as genai
from functools import lru_cache
from typing import Optional, Dict, Any, List
from ..test_mode import is_test_mode, get_test_response


@lru_cache(maxsize=1)
def _configure_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY missing")
    genai.configure(api_key=api_key)
    return True


class GeminiService:
    """Service class for Gemini AI interactions"""
    
    def __init__(self):
        self.model_name = "gemini-1.5-flash"
    
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate content using Gemini AI"""
        if is_test_mode():
            return get_test_response()
        
        try:
            _configure_client()
            model = genai.GenerativeModel(self.model_name)
            
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            
            resp = model.generate_content(full_prompt)
            text = getattr(resp, "text", None)
            
            if text:
                return text
            
            # Fallback assemble from parts
            parts = []
            for cand in getattr(resp, "candidates", []) or []:
                for part in getattr(cand, "content", {}).get("parts", []):
                    val = getattr(part, "text", None) or part.get("text") if isinstance(part, dict) else None
                    if val:
                        parts.append(val)
            
            return "\n".join(parts) if parts else "I'm sorry, I couldn't generate a response right now."
        
        except Exception as e:
            print(f"Error in generate_content: {e}")
            return "I'm sorry, I couldn't generate a response right now. Please check your API keys."
    
    def generate_structured_content(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured JSON content using Gemini AI"""
        if is_test_mode():
            return {"response": get_test_response()}
        
        try:
            response_text = self.generate_content(prompt, system_instruction)
            
            # Try to extract JSON from response
            # Look for JSON between ```json and ``` or just parse the whole response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()
            
            return json.loads(json_text)
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini response: {e}")
            return {"error": "Failed to parse structured response", "raw_response": response_text}
        except Exception as e:
            print(f"Error in generate_structured_content: {e}")
            return {"error": str(e)}


# Singleton instance
_gemini_service_instance: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create the GeminiService singleton instance"""
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService()
    return _gemini_service_instance


def generate_chat_reply(prompt: str, subject: str | None = None) -> str:
    """Generate a chat reply using Gemini AI (backward compatibility function)"""
    service = get_gemini_service()
    system_instruction = f"You are a helpful CS study assistant. Subject: {subject}." if subject else "You are a helpful CS study assistant."
    return service.generate_content(prompt, system_instruction)
