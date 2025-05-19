"""
LLM Connector for fortune telling systems.
Handles interactions with language models.
"""
import os
import json
import logging
import time
import re
import random
from typing import Dict, Any, Optional, List, Tuple, Callable, Generator, Iterator

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
        logger.info(f"Initializing client for provider: {self.provider}")
        
        if self.provider == "openai":
            try:
                import openai
                self.client = openai
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.error("OpenAI package not installed. Install with: pip install openai")
                self.client = None
        elif self.provider == "deepseek":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
                logger.info("DeepSeek client initialized successfully")
            except ImportError:
                logger.error("OpenAI package not installed. Install with: pip install openai")
                self.client = None
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Anthropic client initialized successfully")
            except ImportError:
                logger.error("Anthropic package not installed. Install with: pip install anthropic")
                self.client = None
        elif self.provider == "aws_bedrock":
            try:
                # Try to import and initialize AWSBedrockConnector
                logger.debug("Attempting to import AWS Bedrock connector...")
                from .aws_connector import AWSBedrockConnector
                logger.debug("Import successful, initializing AWS Bedrock connector...")
                self.client = AWSBedrockConnector(self.config)
                logger.info("AWS Bedrock client initialized successfully")
            except ImportError as e:
                logger.error(f"AWS Bedrock connector import error: {str(e)}")
                self.client = None
            except Exception as e:
                logger.error(f"AWS Bedrock connector initialization error: {str(e)}")
                self.client = None
        else:
            logger.warning(f"Unsupported provider: {self.provider}. Using mock client.")
            self.client = None
        
        # Final check to ensure client was properly initialized
        if self.client is None:
            logger.warning(f"Failed to initialize client for provider: {self.provider}")

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
        # Log the prompts for debugging
        logger.info("--- LLM REQUEST BEGIN ---")
        logger.info(f"PROVIDER: {self.provider}")
        logger.info(f"MODEL: {self.model}")
        logger.info("SYSTEM PROMPT:")
        logger.info(system_prompt)
        logger.info("USER PROMPT:")
        logger.info(user_prompt)
        logger.info("--- LLM REQUEST END ---")
        
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
            elif self.provider == "deepseek":
                print("handler determined")
                if self.client is None:
                    logger.warning("DeepSeek client not initialized, falling back to mock connector")
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
        print("function calling OpenAI API")
        if self.client is None:
            return "Error: OpenAI client not initialized", {"error": "Client not initialized"}

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            text_response = response.choices[0].message.content
            print(text_response)
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
        
    def generate_response_streaming(self, 
                                   system_prompt: str, 
                                   user_prompt: str) -> Generator[str, None, None]:
        """
        Generate a streaming response from the LLM, yielding chunks as they become available.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            
        Returns:
            Generator yielding text chunks as they're received
        """
        # Log the prompts for debugging
        logger.info("--- LLM STREAMING REQUEST BEGIN ---")
        logger.info(f"PROVIDER: {self.provider}")
        logger.info(f"MODEL: {self.model}")
        logger.info("SYSTEM PROMPT:")
        logger.info(system_prompt)
        logger.info("USER PROMPT:")
        logger.info(user_prompt)
        logger.info("--- LLM STREAMING REQUEST END ---")
        
        try:
            # Handle provider-specific cases - check AWS first since that's what our config is using
            if self.provider == "aws_bedrock":
                logger.info("Using AWS Bedrock streaming client")
                if self.client is None:
                    logger.warning("AWS Bedrock client not initialized, falling back to mock streaming")
                    yield from self._mock_response_streaming(system_prompt, user_prompt)
                elif hasattr(self.client, 'generate_response_streaming'):
                    logger.info("AWS Bedrock client has streaming support, using it")
                    yield from self.client.generate_response_streaming(system_prompt, user_prompt)
                else:
                    logger.warning("AWS Bedrock client doesn't support streaming, using mock streaming")
                    yield from self._mock_response_streaming(system_prompt, user_prompt)
            elif self.provider == "openai":
                logger.info("Using OpenAI streaming client")
                if self.client is None:
                    logger.warning("OpenAI client not initialized, falling back to mock streaming")
                    yield from self._mock_response_streaming(system_prompt, user_prompt)
                else:
                    yield from self._call_openai_streaming(system_prompt, user_prompt)
            elif self.provider == "deepseek":
                logger.info("Using DeepSeek streaming client")
                if self.client is None:
                    logger.warning("DeepSeek client not initialized, falling back to mock streaming")
                    yield from self._mock_response_streaming(system_prompt, user_prompt)
                else:
                    yield from self._call_openai_streaming(system_prompt, user_prompt)
            elif self.provider == "anthropic" or self.provider == "deepseek":
                logger.info(f"{self.provider} streaming not directly supported, falling back to mock streaming")
                yield from self._mock_response_streaming(system_prompt, user_prompt)
            else:
                # Default to mock streaming responses for unsupported providers
                logger.info(f"Streaming not supported for provider: {self.provider}, using mock streaming")
                yield from self._mock_response_streaming(system_prompt, user_prompt)
                
        except Exception as e:
            logger.error(f"Error generating streaming LLM response: {e}")
            logger.error(f"Exception details: {str(e)}", exc_info=True)
            yield f"Error generating streaming response: {str(e)}"
            
    def _mock_response_streaming(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        """
        Generate a mock streaming response, simulating chunks being received over time.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            
        Returns:
            Generator yielding text chunks
        """
        logger.info("Using mock streaming response generator")
        
        # First get the complete response
        mock = MockConnector()
        full_response, _ = mock.generate_response(system_prompt, user_prompt)
        
        # Add a header indicating this is a mock response - send in two separate chunks
        yield "【注意："
        time.sleep(0.2)
        yield "使用模拟流式输出】"
        time.sleep(0.2)
        yield "\n\n"
        time.sleep(0.3)
        
        # First approach: Character by character with small batches
        # This ensures we have many small chunks for debugging
        response_chars = list(full_response)
        
        # Group into small chunks (2-5 characters)
        batch_size_options = [1, 2, 3, 4, 5]
        position = 0
        
        while position < len(response_chars):
            # Vary the batch size for more realistic effect
            batch_size = min(random.choice(batch_size_options), len(response_chars) - position)
            
            # Extract and yield the next chunk
            current_chunk = ''.join(response_chars[position:position+batch_size])
            yield current_chunk
            
            # Move position forward
            position += batch_size
            
            # Random delay between chunks, increased for smoother reading experience
            time.sleep(random.uniform(0.1, 0.2))  # Increased from 0.05-0.15 range
                
    def generate_best_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        streaming_handler: Callable = None, 
        non_streaming_handler: Callable = None
    ) -> Any:
        """
        智能选择最佳响应生成方式 - 优先使用流式输出，如不可用则退化到标准方式
        
        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            streaming_handler: 处理流式输出的回调函数，接收(response_generator, start_time)参数
            non_streaming_handler: 处理非流式输出的回调函数，接收(response, metadata)参数
        
        Returns:
            完整响应文本或处理后的结果
        """
        # 预先导入所有可能需要的模块
        import time
        import datetime
        
        # 检查是否应该使用流式输出
        use_streaming = os.environ.get("FORTUNE_TELLER_STREAMING", "false").lower() in ("true", "1", "yes")
        
        try:
            if use_streaming and streaming_handler is not None:
                # 记录开始时间
                start_time = time.time()
                
                # 获取流式生成器
                logger.info("使用流式输出生成响应")
                response_generator = self.generate_response_streaming(system_prompt, user_prompt)
                
                # 使用提供的处理函数处理流式输出
                return streaming_handler(response_generator, start_time)
            else:
                # 使用标准方式
                logger.info("使用标准方式生成响应")
                response, metadata = self.generate_response(system_prompt, user_prompt)
                
                # 如果提供了非流式处理函数，使用它
                if non_streaming_handler is not None:
                    return non_streaming_handler(response, metadata)
                return response
        except Exception as e:
            logger.error(f"响应生成出错: {e}", exc_info=True)
            error_message = f"生成响应时出现错误: {str(e)}"
            return error_message

    def _call_openai_streaming(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        """
        Call the OpenAI API with streaming enabled.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            
        Returns:
            Generator yielding text chunks
        """
        if self.client is None:
            yield "Error: OpenAI client not initialized"
            return
            
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Create a streaming response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True  # Enable streaming
            )
            
            # Process the streaming response
            for chunk in response:
                if hasattr(chunk, 'choices') and chunk.choices:
                    choice = chunk.choices[0]
                    if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                        content = choice.delta.content
                        if content is not None:
                            yield content
                            
        except Exception as e:
            logger.error(f"OpenAI streaming API error: {e}")
            yield f"\nError during streaming: {str(e)}"
