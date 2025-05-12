import os
import json
import logging
from typing import Dict, Any, Tuple

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AWSBedrockConnector")
class DeepSeekConnector:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.model = config.get("model", "deepseek-chat")
        self.api_key = self.config.get("api_key") or os.environ.get(f"DEEPSEEK_API_KEY")
        self.temperature = config.get("temperature", 0.7)
        self.tokens = config.get("max_tokens", 2000)

        # Cache for responses
        self.cache = {}

        # Initialize the appropriate client based on the provider
        self._initialize_client()

        logger.info(f"DeepSeek connector initialized with model: {self.model}")

    def _initialize_client(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            self.client = None

    def generate_response(self,
                         system_prompt: str,
                         user_prompt: str) -> Tuple[str, Dict[str, Any]]:
        if self.client is None:
            return "Error: DeepSeek client not initialized", {"error": "Client not initialized"}
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self.tokens,
                temperature=self.temperature,
            )
            text_response = response.choices[0].message.content
            metadata = {
                "finish_reason": response.choices[0].finish_reason,
                "usage": response.usage.to_dict() if hasattr(response.usage, "to_dict") else vars(response.usage),
                "model": response.model
                }
            return text_response, metadata
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error: {str(e)}", {"error": str(e)}

    def set_model(self, model: str) -> None:
        """
        Change the model name.

        Args:
            model: Name of the model
        """
        self.model = model
        logger.info(f"Model changed to {model}")

