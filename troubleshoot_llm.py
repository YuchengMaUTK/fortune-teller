#!/usr/bin/env python3
"""
Troubleshooting script for LLM connectivity issues in Fortune Teller application.
"""
import os
import sys
import yaml
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Troubleshooter")

def check_config_file():
    """Check if config.yaml exists and is properly formatted."""
    config_path = Path("config.yaml")
    example_path = Path("config.yaml.example")
    
    if not config_path.exists():
        if example_path.exists():
            logger.error("config.yaml does not exist! Please create one by copying from config.yaml.example")
            logger.info("You can run: cp config.yaml.example config.yaml")
        else:
            logger.error("Neither config.yaml nor config.yaml.example exists!")
        return None
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Config file found and loaded: {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        return None

def check_llm_config(config):
    """Check if LLM configuration is valid."""
    if not config:
        return False
    
    llm_config = config.get("llm", {})
    provider = llm_config.get("provider")
    
    if not provider:
        logger.error("No LLM provider specified in config.yaml")
        return False
    
    logger.info(f"LLM provider in config: {provider}")
    
    if provider == "openai":
        api_key = llm_config.get("api_key") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI provider specified but no API key found!")
            logger.info("Set OPENAI_API_KEY environment variable or add api_key in config.yaml")
            return False
    
    elif provider == "anthropic":
        api_key = llm_config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("Anthropic provider specified but no API key found!")
            logger.info("Set ANTHROPIC_API_KEY environment variable or add api_key in config.yaml")
            return False
    
    elif provider == "aws_bedrock":
        # Check AWS credentials
        access_key = llm_config.get("aws_access_key") or os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = llm_config.get("aws_secret_key") or os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = llm_config.get("region") or os.environ.get("AWS_REGION")
        
        if not (access_key and secret_key):
            logger.error("AWS Bedrock provider specified but credentials not found!")
            logger.info("Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables or add aws_access_key and aws_secret_key in config.yaml")
            return False
        
        if not region:
            logger.error("AWS Bedrock provider specified but no region found!")
            logger.info("Set AWS_REGION environment variable or add region in config.yaml")
            return False
    
    elif provider == "mock":
        logger.info("Mock provider specified - no API key needed")
        logger.info("This is a test mode that will generate placeholder responses")
        # Mock provider doesn't need any credentials or config
        return True
    
    else:
        logger.warning(f"Unknown provider: {provider}")
        logger.info("Provider should be one of: openai, anthropic, aws_bedrock, mock")
    
    # Check model
    model = llm_config.get("model")
    if not model:
        logger.warning("No model specified in config, will use default model")
    else:
        logger.info(f"Using model: {model}")
    
    return True

def check_dependencies(config=None):
    """
    Check if required Python packages are installed.
    If config is provided, only checks dependencies needed for the configured provider.
    """
    # Always needed
    dependencies = {
        "pyyaml": "pip install pyyaml>=6.0",
    }
    
    # Add provider-specific dependencies
    if config:
        provider = config.get("llm", {}).get("provider")
        if provider == "openai":
            dependencies["openai"] = "pip install openai>=1.0.0"
        elif provider == "anthropic":
            dependencies["anthropic"] = "pip install anthropic>=0.3.0"
        elif provider == "aws_bedrock":
            dependencies["boto3"] = "pip install boto3>=1.28.0"
        elif provider == "mock":
            # Mock provider doesn't need additional dependencies
            pass
    else:
        # If no config is provided, check all potential dependencies
        dependencies.update({
            "openai": "pip install openai>=1.0.0",
            "anthropic": "pip install anthropic>=0.3.0",
            "boto3": "pip install boto3>=1.28.0",
        })
    
    missing = []
    
    for package, install_cmd in dependencies.items():
        try:
            __import__(package)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            logger.warning(f"✗ {package} is not installed")
            missing.append((package, install_cmd))
    
    if missing:
        logger.error("Some required dependencies are missing!")
        logger.info("Install them using the following commands:")
        for _, cmd in missing:
            logger.info(f"  {cmd}")
        
        if "pyyaml" in [pkg for pkg, _ in missing]:
            logger.error("PyYAML is required for basic functionality and configuration!")
        elif config and config.get("llm", {}).get("provider") == "mock":
            logger.info("Note: With mock provider, only pyyaml is strictly required")
            return True  # Consider it OK if using mock provider
    
    return len(missing) == 0

def create_default_config():
    """Create a default config.yaml file from the example if it doesn't exist."""
    config_path = Path("config.yaml")
    example_path = Path("config.yaml.example")
    
    if not config_path.exists() and example_path.exists():
        try:
            # Create a basic config for AWS Bedrock
            with open(example_path, "r") as f:
                example_config = f.read()
            
            with open(config_path, "w") as f:
                f.write(example_config)
            
            logger.info(f"Created default config.yaml from example")
            return True
        except Exception as e:
            logger.error(f"Error creating config file: {e}")
            return False
    
    return False

def main():
    """Run the troubleshooting checks."""
    print("\n=== Fortune Teller LLM Troubleshooting ===\n")
    
    # Check config file first to determine which dependencies we need
    print("\n--- Checking Configuration ---")
    config = check_config_file()
    
    # Check dependencies based on config
    print("\n--- Checking Dependencies ---")
    deps_ok = check_dependencies(config)
    
    if not config and create_default_config():
        print("\n(Created default config.yaml from example)")
        config = check_config_file()
    
    # Check LLM configuration
    if config:
        llm_ok = check_llm_config(config)
    else:
        llm_ok = False
    
    # Summary
    print("\n--- Troubleshooting Summary ---")
    if deps_ok and llm_ok:
        print("✓ All checks passed! Your LLM configuration should work.")
    else:
        print("✗ Some issues were found. Please address them before running the application.")
    
    print("\nFor detailed setup instructions:")
    print("- General LLM setup: See LLM_SETUP_GUIDE.md")
    print("- AWS Bedrock setup: See AWS_CLAUDE_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
