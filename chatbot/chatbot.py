import os
import google.generativeai as genai
import asyncio
from utils.error_handler import ErrorHandler
import logging


class ChatBot:
    def __init__(self, config_manager=None):
        self.config = config_manager
        self._setup_api_key()
        self._setup_model()
        self.response_cache = {}
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()

    def _setup_api_key(self):
        if self.config:
            self.api_key = self.config.get(
                "api_keys.gemini", os.getenv("GEMINI_API_KEY")
            )
        else:
            self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in config or environment")

        genai.configure(api_key=self.api_key)

    def _setup_model(self):
        try:
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.generation_config = genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=25000,
                top_p=0.8,
                top_k=100,
                temperature=0.9,
            )
        except Exception as e:
            error_msg = ErrorHandler.handle_error(e, "setting up Gemini model")
            self.logger.error(error_msg)
            raise

    async def respond_async(self, input_text: str) -> str:
        if not input_text:
            return "I didn't receive any input to respond to."

        # Check cache
        if input_text in self.response_cache:
            self.logger.info("Returning cached response")
            return self.response_cache[input_text]

        try:
            async with self._lock:
                response = await asyncio.to_thread(self.generate_content, input_text)
                reply_text = self._extract_reply(response)

                # Cache the response
                self.response_cache[input_text] = reply_text

                # Limit cache size
                if len(self.response_cache) > 1000:
                    self.response_cache.pop(next(iter(self.response_cache)))

                return reply_text
        except Exception as e:
            error_msg = ErrorHandler.handle_error(e, "generating response")
            self.logger.error(error_msg)
            return "I apologize, but I encountered an error processing your request."

    def generate_content(self, query):
        try:
            return self.model.generate_content(
                query, generation_config=self.generation_config
            )
        except Exception as e:
            raise Exception(f"Error generating content: {e}")

    def _extract_reply(self, response):
        try:
            if hasattr(response, "text"):
                return response.text
            elif isinstance(response, list) and response:
                return response[0].get("text", "")
            return "I couldn't generate a proper response."
        except Exception as e:
            raise Exception(f"Error extracting reply: {e}")

    # Sync version for compatibility
    def respond(self, input_text: str) -> str:
        return asyncio.run(self.respond_async(input_text))
