"""
AWS Bedrock LLM Connector for Fortune Teller application.
"""
import os
import json
import logging
import boto3
import time
import re
from typing import Dict, Any, Tuple, Generator

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AWSBedrockConnector")


class AWSBedrockConnector:
    """
    Connector for AWS Bedrock hosted Anthropic Claude models.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the AWS Bedrock connector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        # Support both direct model IDs and inference profile ARNs
        self.model = self.config.get("model", "anthropic.claude-3-sonnet-20240229-v1:0")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 2000)
        self.region = self.config.get("region", "us-west-2")
        
        # AWS credentials from config or environment variables
        self.aws_access_key = self.config.get("aws_access_key") or os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = self.config.get("aws_secret_key") or os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.aws_session_token = self.config.get("aws_session_token") or os.environ.get("AWS_SESSION_TOKEN")
        
        # Initialize boto3 client
        self._initialize_client()
        
        logger.info(f"AWS Bedrock connector initialized with model: {self.model}")
    
    def _initialize_client(self):
        """Initialize the boto3 client for AWS Bedrock."""
        try:
            # Log the initialization attempt with more details
            logger.info(f"Initializing AWS Bedrock client with region: {self.region}")
            
            # Create boto3 session
            session_args = {
                'region_name': self.region
            }
            
            # Only add credentials if they are provided
            if self.aws_access_key:
                logger.debug("Using provided AWS access key")
                session_args['aws_access_key_id'] = self.aws_access_key
            
            if self.aws_secret_key:
                logger.debug("Using provided AWS secret key")
                session_args['aws_secret_access_key'] = self.aws_secret_key
                
            if self.aws_session_token:
                logger.debug("Using provided AWS session token")
                session_args['aws_session_token'] = self.aws_session_token
                
            # Create the session
            session = boto3.Session(**session_args)
            
            # Get credentials used by the session for debugging
            creds = session.get_credentials()
            if creds:
                logger.debug(f"Session created with credentials from: {creds.method}")
            else:
                logger.warning("Session created but no credentials were found")
            
            # Create the bedrock-runtime client
            self.client = session.client('bedrock-runtime')
            
            # Verify the client by making a simple API call
            try:
                self.client.list_model_customization_jobs(maxResults=1)
                logger.info("AWS Bedrock client verified and ready to use")
            except Exception as verify_error:
                # This is expected to fail with access denied if the user doesn't have permission,
                # but it proves the client can make API calls
                if "AccessDenied" in str(verify_error):
                    logger.info("Client initialized (limited permissions detected)")
                else:
                    logger.warning(f"Client initialized but verification failed: {verify_error}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize AWS Bedrock client: {e}")
            import traceback
            logger.debug(f"AWS client initialization traceback: {traceback.format_exc()}")
            self.client = None
    
    def generate_response(self, 
                         system_prompt: str, 
                         user_prompt: str) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response from the AWS-hosted Anthropic Claude model.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            
        Returns:
            Tuple of (text response, metadata)
        """
        # Log the prompts for AWS Bedrock debugging
        logger.info("--- AWS BEDROCK REQUEST BEGIN ---")
        logger.info(f"MODEL: {self.model}")
        logger.info(f"REGION: {self.region}")
        logger.info("SYSTEM PROMPT:")
        logger.info(system_prompt)
        logger.info("USER PROMPT:")
        logger.info(user_prompt)
        logger.info("--- AWS BEDROCK REQUEST END ---")
        
        if self.client is None:
            return "Error: AWS Bedrock client not initialized", {"error": "Client not initialized"}
        
        try:
            # Format the request body for Claude model on AWS Bedrock
            # Check if we're using Claude 3.7
            is_claude_3_7 = "claude-3-7" in self.model.lower()
            
            if is_claude_3_7:
                # Special format for Claude 3.7
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "top_k": 250,
                    "stop_sequences": [],
                    "temperature": self.temperature,
                    "top_p": 0.999,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": user_prompt
                                }
                            ]
                        }
                    ]
                }
                
                # Add system prompt if provided
                if system_prompt:
                    request_body["system"] = system_prompt
            else:
                # Standard format for other Claude models
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    "system": system_prompt  # For AWS Bedrock, system prompt is a separate field
                }
            
            # Determine if this is a model ID or inference profile ARN
            if self.model.startswith("arn:"):
                # Use inference profile ARN
                response = self.client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json"
                )
                
                # Parse the non-streaming response
                raw_response = response['body'].read()
                logger.debug(f"Raw response from AWS Bedrock: {raw_response}")
                
                try:
                    response_body = json.loads(raw_response)
                    logger.debug(f"Parsed response body: {json.dumps(response_body, indent=2)}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse response as JSON: {e}")
                    return f"Error parsing response from AWS Bedrock: {str(e)}", {"error": str(e)}
                
                # Debug log the entire response structure
                logger.info(f"AWS Bedrock response structure: {json.dumps(response_body, indent=2)}")
                
                # Handle different response formats based on the model and response structure
                if "completion" in response_body:
                    # Some inference profiles return in this format
                    text_response = response_body.get("completion", "")
                    logger.info("Using 'completion' field from response")
                elif "content" in response_body:
                    if isinstance(response_body["content"], list):
                        content_items = response_body["content"]
                        text_pieces = []
                        
                        for item in content_items:
                            if isinstance(item, dict):
                                if item.get("type") == "text" and "text" in item:
                                    text_pieces.append(item["text"])
                            elif isinstance(item, str):
                                text_pieces.append(item)
                        
                        if text_pieces:
                            text_response = "\n".join(text_pieces)
                            logger.info("Extracted text from content list items")
                        else:
                            text_response = f"Response format not recognized. Please check logs."
                            logger.warning(f"Could not extract text from content: {response_body}")
                    elif isinstance(response_body["content"], dict) and "text" in response_body["content"]:
                        # Another potential format
                        text_response = response_body["content"]["text"]
                        logger.info("Using text from content dictionary")
                    else:
                        text_response = f"Unsupported response format: {response_body}"
                        logger.warning(f"Unrecognized content format in response")
                else:
                    # If we can't find any recognized structure, return raw body as string
                    text_response = f"Unsupported response format from AWS Bedrock. Raw response: {raw_response}"
                    logger.warning(f"Unrecognized response format from AWS Bedrock")
                
                metadata = {
                    "model": self.model,
                    "finish_reason": "unknown",  # Streaming doesn't provide this directly
                    "usage": {}  # Streaming doesn't provide usage information
                }
            else:
                # Use direct model ID
                try:
                    response = self.client.invoke_model(
                        modelId=self.model,
                        body=json.dumps(request_body)
                    )
                    
                    # Parse the response
                    response_body = json.loads(response['body'].read())
                    text_response = response_body['content'][0]['text']
                    
                    metadata = {
                        "model": self.model,
                        "finish_reason": response_body.get('stop_reason', 'unknown'),
                        "usage": response_body.get('usage', {})
                    }
                except Exception as e:
                    # If direct invocation fails, suggest using inference profiles
                    if "on-demand throughput isn't supported" in str(e):
                        error_msg = (
                            f"Error: 无法直接调用模型 {self.model}。AWS Bedrock 要求使用推理配置文件。\n"
                            f"您需要在 AWS Bedrock 中创建一个推理配置文件，并使用该配置文件的 ARN 而不是直接使用模型 ID。\n"
                            f"请参考项目根目录下的 INFERENCE_PROFILE_SETUP.md 文件了解如何创建推理配置文件。\n\n"
                            f"推理配置文件 ARN 格式应为: arn:aws:bedrock:[region]:[account]:inference-profile/[profile-name]\n"
                            f"请在 config.yaml 文件中更新 model 参数以使用推理配置文件 ARN。"
                        )
                        logger.error(error_msg)
                        return error_msg, {"error": str(e)}
                    else:
                        # Re-raise if it's a different error
                        raise
            
            return text_response, metadata
            
        except Exception as e:
            error_msg = f"AWS Bedrock API error: {str(e)}"
            logger.error(error_msg)
            return f"Error: {str(e)}", {"error": str(e)}
    
    def set_model(self, model: str) -> None:
        """
        Change the model name.
        
        Args:
            model: Name of the model
        """
        self.model = model
        logger.info(f"Model changed to {model}")
    
    def set_region(self, region: str) -> None:
        """
        Change the AWS region.
        
        Args:
            region: AWS region name
        """
        self.region = region
        # Re-initialize the client with new region
        self._initialize_client()
        logger.info(f"AWS region changed to {region}")
        
    def generate_response_streaming(self, 
                                   system_prompt: str, 
                                   user_prompt: str) -> Generator[str, None, None]:
        """
        Generate a streaming response from AWS Bedrock.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            
        Returns:
            Generator yielding text chunks as they become available
        """
        # Log the prompts for AWS Bedrock debugging
        logger.info("--- AWS BEDROCK STREAMING REQUEST BEGIN ---")
        logger.info(f"MODEL: {self.model}")
        logger.info(f"REGION: {self.region}")
        logger.info("SYSTEM PROMPT:")
        logger.info(system_prompt)
        logger.info("USER PROMPT:")
        logger.info(user_prompt)
        logger.info("--- AWS BEDROCK STREAMING REQUEST END ---")
        
        if self.client is None:
            yield "Error: AWS Bedrock client not initialized"
            return
        
        try:
            # Format the request body for Claude model on AWS Bedrock
            # Check if we're using Claude 3.7
            is_claude_3_7 = "claude-3-7" in self.model.lower()
            
            if is_claude_3_7:
                # Special format for Claude 3.7
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "top_k": 250,
                    "stop_sequences": [],
                    "temperature": self.temperature,
                    "top_p": 0.999,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": user_prompt
                                }
                            ]
                        }
                    ]
                }
                
                # Add system prompt if provided
                if system_prompt:
                    request_body["system"] = system_prompt
            else:
                # Standard format for other Claude models
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    "system": system_prompt  # For AWS Bedrock, system prompt is a separate field
                }
            
            # Determine if this is a model ID or inference profile ARN
            if self.model.startswith("arn:"):
                # Use inference profile ARN with streaming
                try:
                    logger.debug(f"Attempting streaming with inference profile ARN: {self.model}")
                    logger.debug(f"Request body: {json.dumps(request_body, indent=2)}")
                    
                    try:
                        response_stream = self.client.invoke_model_with_response_stream(
                            modelId=self.model,
                            body=json.dumps(request_body),
                            contentType="application/json",
                            accept="application/json"
                        )
                        logger.debug("Successfully initiated streaming response")
                    except Exception as e:
                        logger.error(f"Error initiating streaming: {str(e)}")
                        if "not supported" in str(e).lower() or "unsupported" in str(e).lower():
                            logger.warning("This inference profile may not support streaming. Falling back to non-streaming method.")
                            yield "【提示：此推理配置文件不支持流式输出，已退化为模拟流式】\n\n"
                            
                            # Fall back to non-streaming method and simulate streaming
                            text_response, _ = self.generate_response(system_prompt, user_prompt)
                            sentences = re.split(r'([.!?。！？]+\s*)', text_response)
                            for i in range(0, len(sentences), 2):
                                if i < len(sentences):
                                    chunk = sentences[i]
                                    if i+1 < len(sentences):
                                        chunk += sentences[i+1]
                                    if chunk.strip():
                                        yield chunk
                                        time.sleep(0.05)
                            return
                        else:
                            # Re-raise if it's a different error
                            raise
                    
                    # Process the streaming response
                    logger.debug("Processing streaming response events")
                    event_count = 0
                    for event in response_stream.get("body", []):
                        event_count += 1
                        if "chunk" in event:
                            try:
                                raw_bytes = event["chunk"]["bytes"]
                                logger.debug(f"Received chunk {event_count}: {raw_bytes[:100]}...")
                                chunk_data = json.loads(raw_bytes)
                                
                                # Handle Claude 3.7+ JSON streaming format
                                if "type" in chunk_data:
                                    # This is the newer JSON streaming format
                                    if chunk_data["type"] == "content_block_delta":
                                        if "delta" in chunk_data and "text" in chunk_data["delta"]:
                                            yield chunk_data["delta"]["text"]
                                    # Skip other message types like message_start, content_block_start, etc.
                                    continue
                                
                                # Handle older response formats
                                if "completion" in chunk_data:
                                    # Claude 1/2 style
                                    yield chunk_data["completion"]
                                elif "content" in chunk_data:
                                    if isinstance(chunk_data["content"], list):
                                        # Claude 3 style with content list
                                        for content_item in chunk_data["content"]:
                                            if isinstance(content_item, dict) and content_item.get("type") == "text":
                                                yield content_item["text"]
                                            elif isinstance(content_item, str):
                                                yield content_item
                                    elif isinstance(chunk_data["content"], str):
                                        # Some formats might have direct string content
                                        yield chunk_data["content"]
                                    elif isinstance(chunk_data["content"], dict) and "text" in chunk_data["content"]:
                                        # Yet another possible format
                                        yield chunk_data["content"]["text"]
                                else:
                                    # Log the unknown format but don't yield it to avoid showing JSON to users
                                    logger.warning(f"Unknown chunk format: {json.dumps(chunk_data)[:200]}")
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse chunk as JSON: {event['chunk']['bytes'][:200]}")
                                # Don't yield raw bytes to avoid showing gibberish to users
                except Exception as e:
                    error_msg = f"Error during AWS Bedrock streaming: {str(e)}"
                    logger.error(error_msg)
                    yield f"\n{error_msg}"
            else:
                
                # Try to use non-streaming API and simulate streaming
                try:
                    # Get complete response
                    text_response, _ = self.generate_response(system_prompt, user_prompt)
                    
                    # Simulate streaming by yielding chunks of the response
                    import re
                    # Split by sentences for Chinese and English
                    sentences = re.split(r'([.!?。！？]+\s*)', text_response)
                    
                    # Yield each sentence (with its punctuation if available)
                    for i in range(0, len(sentences), 2):
                        if i < len(sentences):
                            chunk = sentences[i]
                            if i+1 < len(sentences):  # Add punctuation if available
                                chunk += sentences[i+1]
                            if chunk.strip():  # Only yield non-empty chunks
                                yield chunk
                                # Small delay to simulate streaming
                                import time
                                time.sleep(0.05)
                except Exception as e:
                    error_msg = f"Error during simulated streaming: {str(e)}"
                    logger.error(error_msg)
                    yield f"\n{error_msg}"
        except Exception as e:
            error_msg = f"AWS Bedrock streaming API error: {str(e)}"
            logger.error(error_msg)
            yield f"\nError during streaming: {str(e)}"
