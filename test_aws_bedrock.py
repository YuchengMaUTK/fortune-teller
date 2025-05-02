#!/usr/bin/env python3
"""
Test script to verify AWS Bedrock Claude integration.
"""
import os
import yaml
import sys
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AWSBedrockTest")

# Add parent directory to path so we can import from fortune_teller
sys.path.append('.')

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

def main():
    """Test AWS Bedrock Claude integration."""
    print("\n=== Testing AWS Bedrock Claude Integration ===\n")
    
    # Check AWS environment variables
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_region = os.environ.get("AWS_REGION")
    
    print("AWS Credentials Check:")
    print(f"- AWS_ACCESS_KEY_ID: {'Set' if aws_access_key else 'Not set'}")
    print(f"- AWS_SECRET_ACCESS_KEY: {'Set' if aws_secret_key else 'Not set'}")
    print(f"- AWS_REGION: {aws_region or 'Not set'}")
    
    # Load config
    config = load_config()
    llm_config = config.get("llm", {})
    
    if llm_config:
        print("\nLLM Configuration:")
        print(f"- Provider: {llm_config.get('provider')}")
        print(f"- Model: {llm_config.get('model')}")
        print(f"- Region: {llm_config.get('region', aws_region)}")
    
    # Test AWS Bedrock connector
    try:
        print("\nAttempting to import and initialize AWS Bedrock connector...")
        from fortune_teller.core.aws_connector import AWSBedrockConnector
        
        # Create AWS Bedrock connector
        connector = AWSBedrockConnector(llm_config)
        print(f"AWS Bedrock connector initialized")
        
        # Check if client was initialized successfully
        if connector.client is None:
            print("❌ AWS Bedrock client initialization failed!")
            print("Please check your AWS credentials and region")
            return
        
        # Test simple prompt
        print("\nTesting prompt generation (this may take a moment)...")
        response, metadata = connector.generate_response(
            "You are a helpful assistant.",
            "Tell me a short joke about fortune telling."
        )
        
        print("\nResponse received!")
        print(f"\nModel: {metadata.get('model')}")
        print("Response:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        print(f"\nTest completed successfully! AWS Bedrock integration is working.")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've installed the required dependencies:")
        print("  pip install boto3>=1.28.0")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your AWS credentials and ensure you have the necessary permissions.")

if __name__ == "__main__":
    main()
