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
        if self.client is None:
            return "Error: AWS Bedrock client not initialized", {"error": "Client not initialized"}
        
        try:
            # Format the request body for Claude model on AWS Bedrock
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
                response = self.client.invoke_model_with_response_stream(
                    modelId=self.model,
                    body=json.dumps(request_body)
                )
                # For streaming response, we need to collect all chunks
                response_body = {"content": []}
                for event in response["body"]:
                    chunk = json.loads(event["chunk"]["bytes"])
                    if "content" in chunk and chunk["content"]:
                        response_body["content"].extend(chunk["content"])
                
                # Extract text from content
                if response_body["content"] and "text" in response_body["content"][0]:
                    text_response = response_body["content"][0]["text"]
                else:
                    text_response = "No text content received from model"
                
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
                            f"Error: The model {self.model} cannot be invoked directly. "
                            f"You need to create an inference profile for this model in AWS Bedrock "
                            f"and use the inference profile ARN instead. See AWS_CLAUDE_SETUP_GUIDE.md "
                            f"for more information."
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
