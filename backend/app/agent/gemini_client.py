"""LLM client using Groq for generating natural language responses."""
import asyncio
from functools import partial
from groq import Groq
from app.config import get_settings

# System prompt that defines the agent's persona
SYSTEM_PROMPT = """You are an expert financial portfolio advisor AI assistant working for a B2B wealth management platform in India.

Your responsibilities:
- Analyze portfolio data and provide clear, actionable insights
- Explain financial metrics (XIRR, CAGR, P&L) in simple terms
- Provide risk analysis and rebalancing recommendations
- Answer compliance questions using SEBI guidelines context
- Be professional yet conversational, use INR for all currency values
- Format responses with markdown: use **bold** for key metrics, bullet points for lists
- Keep responses concise but informative — aim for 3-6 sentences for simple queries, more for detailed analysis
- When showing numbers, always format them with commas (e.g., INR 14,90,769)
- If you don't have enough data to answer, say so honestly

You are given structured data from the portfolio database as context. Use this data to generate your response.
Do NOT fabricate any numbers — only use the data provided to you."""


class LLMClient:
    """Wrapper around Groq API for portfolio agent responses."""

    def __init__(self):
        self._client = None
        self._available = None  # None = not yet checked

    def _ensure_client(self) -> bool:
        """Lazy-initialize the Groq client on first use."""
        if self._available is not None:
            return self._available

        settings = get_settings()
        api_key = settings.groq_api_key
        if not api_key:
            print("[LLM] Warning: GROQ_API_KEY not set. LLM responses disabled.")
            self._available = False
            return False

        try:
            self._client = Groq(api_key=api_key)
            self._available = True
            print(f"[LLM] Groq client initialized (key: {api_key[:8]}...)")
            return True
        except Exception as e:
            print(f"[LLM] Groq client init error: {e}")
            self._available = False
            return False

    @property
    def is_available(self) -> bool:
        return self._ensure_client()

    def _call_llm(self, prompt: str) -> str:
        """Synchronous Groq API call."""
        response = self._client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_completion_tokens=1500,
        )
        return response.choices[0].message.content

    async def generate_response(
        self,
        user_message: str,
        structured_data: str,
        task_context: str = "",
    ) -> str | None:
        """
        Generate a natural language response using Groq.

        Returns:
            Generated response string, or None if generation fails (caller should use fallback)
        """
        if not self.is_available:
            return None

        prompt = f"""Task: {task_context}

User's question: {user_message}

Here is the relevant data from the portfolio management system:

{structured_data}

Based on this data, provide a helpful, conversational response to the user's question. Use the exact numbers from the data — do not make up any figures."""

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, partial(self._call_llm, prompt))
            print(f"[LLM] Groq response generated ({len(result)} chars)")
            return result
        except Exception as e:
            print(f"[LLM] Groq error: {type(e).__name__}: {e}")
            return None


# Singleton — imported by portfolio_agent.py as `gemini_client` (name kept for compatibility)
gemini_client = LLMClient()
