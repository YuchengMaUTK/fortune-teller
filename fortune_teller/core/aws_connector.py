"""
AWS Bedrock LLM Connector for Fortune Teller application.
"""
import os
import json
import logging
import boto3
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

        Credential resolution order (boto3 default chain):
          1. Explicit keys in config.yaml (aws_access_key / aws_secret_key).
          2. `profile:` named in config.yaml -> ~/.aws/credentials or ~/.aws/config.
          3. Standard env vars AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY /
             AWS_SESSION_TOKEN / AWS_PROFILE.
          4. Default profile in ~/.aws/credentials, SSO, IMDS, etc.

        Region is taken from config, env AWS_REGION / AWS_DEFAULT_REGION,
        or the profile's configured region.
        """
        self.config = config or {}
        # Support both direct model IDs and inference profile ARNs
        self.model = self.config.get("model", "anthropic.claude-3-sonnet-20240229-v1:0")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 2000)
        self.region = (
            self.config.get("region")
            or os.environ.get("AWS_REGION")
            or os.environ.get("AWS_DEFAULT_REGION")
        )
        self.profile = self.config.get("profile") or os.environ.get("AWS_PROFILE")

        # Explicit keys from config (env vars are handled natively by boto3).
        self.aws_access_key = self.config.get("aws_access_key")
        self.aws_secret_key = self.config.get("aws_secret_key")
        self.aws_session_token = self.config.get("aws_session_token")

        self._initialize_client()

        logger.info(f"AWS Bedrock connector initialized with model: {self.model}")

    def _initialize_client(self):
        """Initialize the boto3 client for AWS Bedrock."""
        try:
            session_args: Dict[str, Any] = {}
            if self.region:
                session_args["region_name"] = self.region
            if self.profile and not self.aws_access_key:
                # Explicit keys take precedence; otherwise use the named profile.
                session_args["profile_name"] = self.profile
            if self.aws_access_key:
                session_args["aws_access_key_id"] = self.aws_access_key
            if self.aws_secret_key:
                session_args["aws_secret_access_key"] = self.aws_secret_key
            if self.aws_session_token:
                session_args["aws_session_token"] = self.aws_session_token

            session = boto3.Session(**session_args)

            creds = session.get_credentials()
            if creds is None:
                logger.error(
                    "No AWS credentials found. Set env vars, configure "
                    "~/.aws/credentials, or add `profile:` to config.yaml."
                )
                self.client = None
                return

            logger.info(
                f"AWS session ready (source={creds.method}, "
                f"region={session.region_name or 'unset'}, "
                f"profile={self.profile or 'default'})"
            )
            self.client = session.client("bedrock-runtime")

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

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": user_prompt}],
            "system": system_prompt,
        }

        try:
            response = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            )
            response_body = json.loads(response["body"].read())
            text_response = "".join(
                block["text"]
                for block in response_body.get("content", [])
                if isinstance(block, dict) and block.get("type") == "text"
            )
            metadata = {
                "model": self.model,
                "finish_reason": response_body.get("stop_reason", "unknown"),
                "usage": response_body.get("usage", {}),
            }
            return text_response, metadata
        except Exception as e:
            error_msg = f"AWS Bedrock API error: {e}"
            logger.error(error_msg)
            return f"Error: {e}", {"error": str(e)}
    
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

        # Every current Bedrock Claude variant accepts the same Messages body
        # and supports invoke_model_with_response_stream — direct model IDs,
        # cross-region inference profile IDs (us.*, eu.*), and full ARNs.
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": user_prompt}],
            "system": system_prompt,
        }

        try:
            response_stream = self.client.invoke_model_with_response_stream(
                modelId=self.model,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            )
        except Exception as e:
            logger.error(f"Bedrock streaming request failed: {e}")
            yield f"\nError: {e}"
            return

        for event in response_stream.get("body", []):
            if "chunk" not in event:
                continue
            try:
                chunk_data = json.loads(event["chunk"]["bytes"])
            except json.JSONDecodeError:
                logger.warning("Failed to parse chunk JSON; skipping")
                continue

            # Anthropic-on-Bedrock streaming events. We only care about
            # content_block_delta -> delta.text; message_start,
            # content_block_start, message_stop, etc. carry no text.
            if chunk_data.get("type") == "content_block_delta":
                delta = chunk_data.get("delta", {})
                text = delta.get("text")
                if text:
                    yield text
