import os
import google.generativeai as genai
from functools import lru_cache
from ..test_mode import is_test_mode, get_test_response


@lru_cache(maxsize=1)
def _configure_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY missing")
    genai.configure(api_key=api_key)
    return True


def generate_chat_reply(prompt: str, subject: str | None = None) -> str:
    # Check if in test mode
    if is_test_mode():
        return get_test_response()
    
    try:
        _configure_client()
        model = genai.GenerativeModel("gemini-1.5-flash")
        system_prefix = f"You are a helpful CS study assistant. Subject: {subject}. " if subject else "You are a helpful CS study assistant. "
        full_prompt = system_prefix + prompt
        resp = model.generate_content(full_prompt)
        # google-generativeai returns candidates; use text convenience
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
        print(f"Error in generate_chat_reply: {e}")
        return "I'm sorry, I couldn't generate a response right now. Please check your API keys."
