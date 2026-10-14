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
        self.client = None
        try:
            self._initialize_client()
        except Exception as exc:
            logger.error("LLM client initialization failed: %s", exc)

        logger.info(f"LLM Connector initialized with provider: {self.provider}, model: {self.model}")

    def _initialize_client(self):
        """Initialize the appropriate client based on the provider."""
        logger.info(f"Initializing client for provider: {self.provider}")
        
        if self.provider == "openai":
            try:
                from openai import OpenAI, OpenAIError
                try:
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info("OpenAI client initialized successfully")
                except OpenAIError as e:
                    logger.error(f"OpenAI client init failed: {e}")
                    self.client = None
            except ImportError:
                logger.error("openai package not installed. Install with: pip install openai")
                self.client = None
        elif self.provider == "deepseek":
            try:
                from openai import OpenAI, OpenAIError
                try:
                    self.client = OpenAI(
                        api_key=self.api_key, base_url="https://api.deepseek.com"
                    )
                    logger.info("DeepSeek client initialized successfully")
                except OpenAIError as e:
                    logger.error(f"DeepSeek client init failed: {e}")
                    self.client = None
            except ImportError:
                logger.error("openai package not installed. Install with: pip install openai")
                self.client = None
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Anthropic client initialized successfully")
            except ImportError:
                logger.error("anthropic package not installed. Install with: pip install anthropic")
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
        elif self.provider == "mock":
            self.client = MockConnector()
        else:
            logger.warning(f"Unsupported provider: {self.provider}.")
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
        logger.info("--- LLM REQUEST END ---")
        
        # Generate a cache key
        cache_key = self._generate_cache_key(system_prompt, user_prompt)

        # Check cache if enabled
        if use_cache and cache_key in self.cache:
            logger.info("Using cached response")
            return self.cache[cache_key]

        if self.provider not in {"openai", "deepseek", "anthropic", "aws_bedrock", "mock"}:
            error = f"Unsupported LLM provider: {self.provider}"
            return f"Error: {error}", {"error": error}
        if self.client is None:
            error = f"{self.provider} client not initialized; check credentials and provider dependencies"
            return f"Error: {error}", {"error": error}

        try:
            if self.provider in {"openai", "deepseek"}:
                response = self._call_openai(system_prompt, user_prompt)
            elif self.provider == "anthropic":
                response = self._call_anthropic(system_prompt, user_prompt)
            elif self.provider == "aws_bedrock":
                response = self.client.generate_response(system_prompt, user_prompt)
            else:
                text, metadata = self._mock_response(system_prompt, user_prompt)
                response = ("[MOCK] " + text, {**metadata, "mock": True})

            # Cache the response
            if use_cache and "error" not in response[1]:
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

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            text_response = response.choices[0].message.content
            usage = response.usage
            metadata = {
                "finish_reason": response.choices[0].finish_reason,
                "usage": usage.model_dump() if hasattr(usage, "model_dump") else vars(usage),
                "model": response.model,
            }

            return text_response, metadata

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error: {str(e)}", {"error": str(e)}

    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Call the Anthropic Messages API (Claude 3+)."""
        if self.client is None:
            return "Error: Anthropic client not initialized", {"error": "Client not initialized"}

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            text_response = "".join(
                block.text for block in response.content if getattr(block, "type", None) == "text"
            )
            metadata = {
                "stop_reason": response.stop_reason,
                "model": response.model,
                "usage": response.usage.model_dump()
                if hasattr(response.usage, "model_dump")
                else vars(response.usage),
            }

            return text_response, metadata

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error: {str(e)}", {"error": str(e)}

    def _call_anthropic_streaming(
        self, system_prompt: str, user_prompt: str
    ) -> Generator[str, None, None]:
        """Stream text chunks from Anthropic Messages API."""
        if self.client is None:
            yield "Error: Anthropic client not initialized"
            return

        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            yield f"\nError during streaming: {str(e)}"

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
        self.client = None
        try:
            self._initialize_client()
        except Exception as exc:
            logger.error("LLM client initialization failed: %s", exc)

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
        logger.info("--- LLM STREAMING REQUEST END ---")
        
        if self.provider not in {"openai", "deepseek", "anthropic", "aws_bedrock", "mock"}:
            yield f"Error: Unsupported LLM provider: {self.provider}"
            return
        if self.client is None:
            yield f"Error: {self.provider} client not initialized; check credentials and provider dependencies"
            return

        try:
            if self.provider == "aws_bedrock":
                yield from self.client.generate_response_streaming(system_prompt, user_prompt)
            elif self.provider in {"openai", "deepseek"}:
                yield from self._call_openai_streaming(system_prompt, user_prompt)
            elif self.provider == "anthropic":
                yield from self._call_anthropic_streaming(system_prompt, user_prompt)
            else:
                text, _ = self._mock_response(system_prompt, user_prompt)
                yield "[MOCK] " + text

        except Exception as e:
            logger.error(f"Error generating streaming LLM response: {e}")
            logger.error(f"Exception details: {str(e)}", exc_info=True)
            yield f"Error generating streaming response: {str(e)}"
            
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
        
        # Streaming is on by default; set FORTUNE_TELLER_STREAMING=false to disable.
        use_streaming = os.environ.get("FORTUNE_TELLER_STREAMING", "true").lower() in ("true", "1", "yes")
        
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
