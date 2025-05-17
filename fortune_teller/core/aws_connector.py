"""
AWS Bedrock LLM Connector for Fortune Teller application.
"""
import os
import json
import logging
import boto3
from typing import Dict, Any, Tuple

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
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                aws_session_token=self.aws_session_token,
                region_name=self.region
            )
            
            self.client = session.client('bedrock-runtime')
            logger.info("AWS Bedrock client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Bedrock client: {e}")
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
