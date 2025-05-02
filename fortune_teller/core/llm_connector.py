"""
LLM Connector for fortune telling systems.
Handles interactions with language models.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple, Callable

from .mock_connector import MockConnector

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LLMConnector")


class LLMConnector:
    """
    Connector for Language Learning Models (LLMs).
    Handles sending prompts to LLMs and processing their responses.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the LLM connector.
        
        Args:
            config: Configuration dictionary for the LLM connector
        """
        self.config = config or {}
        self.provider = self.config.get("provider", "openai")
        self.model = self.config.get("model", "gpt-4")
        self.api_key = self.config.get("api_key") or os.environ.get(f"{self.provider.upper()}_API_KEY")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 2000)
        
        # Cache for responses
        self.cache = {}
        
        # Initialize the appropriate client based on the provider
        self._initialize_client()
        
        logger.info(f"LLM Connector initialized with provider: {self.provider}, model: {self.model}")
    
    def _initialize_client(self):
        """Initialize the appropriate client based on the provider."""
        if self.provider == "openai":
            try:
                import openai
                openai.api_key = self.api_key
                self.client = openai
            except ImportError:
                logger.error("OpenAI package not installed. Install with: pip install openai")
                self.client = None
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                logger.error("Anthropic package not installed. Install with: pip install anthropic")
                self.client = None
        elif self.provider == "aws_bedrock":
            try:
                from .aws_connector import AWSBedrockConnector
                self.client = AWSBedrockConnector(self.config)
            except ImportError:
                logger.error("AWS Bedrock connector not available. Check boto3 installation.")
                self.client = None
        else:
            logger.warning(f"Unsupported provider: {self.provider}. Using mock client.")
            self.client = None
    
    def generate_response(self, 
                        system_prompt: str, 
                        user_prompt: str, 
                        use_cache: bool = True) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response from the LLM.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            use_cache: Whether to use cached responses
            
        Returns:
            Tuple of (text response, metadata)
        """
        # Generate a cache key
        cache_key = self._generate_cache_key(system_prompt, user_prompt)
        
        # Check cache if enabled
        if use_cache and cache_key in self.cache:
            logger.info("Using cached response")
            return self.cache[cache_key]
        
        try:
            # Handle provider-specific cases
            if self.provider == "openai":
                if self.client is None:
                    logger.warning("OpenAI client not initialized, falling back to mock connector")
                    response = self._mock_response(system_prompt, user_prompt)
                else:
                    response = self._call_openai(system_prompt, user_prompt)
            elif self.provider == "anthropic":
                if self.client is None:
                    logger.warning("Anthropic client not initialized, falling back to mock connector")
                    response = self._mock_response(system_prompt, user_prompt)
                else:
                    response = self._call_anthropic(system_prompt, user_prompt)
            elif self.provider == "aws_bedrock":
                if self.client is None:
                    logger.warning("AWS Bedrock client not initialized, falling back to mock connector")
                    response = self._mock_response(system_prompt, user_prompt)
                else:
                    response = self.client.generate_response(system_prompt, user_prompt)
            else:
                # Default to mock responses for unknown providers
                logger.info(f"Using mock connector for provider: {self.provider}")
                response = self._mock_response(system_prompt, user_prompt)
            
            # Cache the response
            if use_cache:
                self.cache[cache_key] = response
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return f"Error: {str(e)}", {"error": str(e)}
    
    def _generate_cache_key(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a cache key for the given prompts."""
        combined = f"{self.provider}_{self.model}_{system_prompt}_{user_prompt}"
        return str(hash(combined))
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Call the OpenAI API with the given prompts."""
        if self.client is None:
            return "Error: OpenAI client not initialized", {"error": "Client not initialized"}
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
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
    
    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Call the Anthropic API with the given prompts."""
        if self.client is None:
            return "Error: Anthropic client not initialized", {"error": "Client not initialized"}
        
        try:
            prompt = f"{self.client.HUMAN_PROMPT} {user_prompt} {self.client.AI_PROMPT}"
            
            response = self.client.completions.create(
                prompt=prompt,
                model=self.model,
                max_tokens_to_sample=self.max_tokens,
                temperature=self.temperature
            )
            
            text_response = response.completion
            metadata = {
                "stop_reason": response.stop_reason,
                "model": response.model
            }
            
            return text_response, metadata
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error: {str(e)}", {"error": str(e)}
    
    def _mock_response(self, system_prompt: str, user_prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a mock response using the MockConnector."""
        # Use the more sophisticated mock connector
        mock = MockConnector()
        return mock.generate_response(system_prompt, user_prompt)
    
    def set_provider(self, provider: str, api_key: Optional[str] = None) -> bool:
        """
        Change the LLM provider.
        
        Args:
            provider: Name of the provider
            api_key: API key for the provider
            
        Returns:
            True if successful, False otherwise
        """
        self.provider = provider
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get(f"{provider.upper()}_API_KEY")
        
        # Clear cache when changing provider
        self.cache = {}
        
        # Re-initialize client
        self._initialize_client()
        
        logger.info(f"Provider changed to {provider}")
        return self.client is not None
    
    def set_model(self, model: str) -> None:
        """
        Change the model name.
        
        Args:
            model: Name of the model
        """
        self.model = model
        logger.info(f"Model changed to {model}")
        
        # Clear cache when changing model
        self.cache = {}
