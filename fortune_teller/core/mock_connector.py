"""
Mock LLM Connector for fortune telling systems.
Used as a fallback when no real LLM is available.
"""
import logging
import random
from typing import Dict, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MockConnector")


class MockConnector:
    """
    Mock connector that simulates LLM responses.
    Used for testing or when no LLM provider is available.
    """
    
    def __init__(self):
        """Initialize the mock connector."""
        logger.info("Mock LLM connector initialized")
    
    def generate_response(self, 
                        system_prompt: str, 
                        user_prompt: str) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a mock response.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            
        Returns:
            Tuple of (text response, metadata)
        """
        logger.warning("Using mock LLM response - this is only for testing!")
        
        # Extract any fortune system name mentioned in the prompt
        system_name = "算命系统"
        if "八字" in system_prompt or "八字" in user_prompt:
            system_name = "八字命理"
        elif "塔罗" in system_prompt or "塔罗" in user_prompt:
            system_name = "塔罗牌"
        elif "星座" in system_prompt or "星座" in user_prompt or "占星" in system_prompt or "占星" in user_prompt:
            system_name = "星座占星"
        
        # Generic fortune telling responses
        responses = [
            f"这是一个来自{system_name}的模拟解读结果。在实际使用时，这里会显示由LLM生成的专业解读内容。",
            "## 总体运势\n\n这是一个模拟的运势分析，用于测试系统功能。实际使用时，这里将显示基于您输入信息的详细解读。",
            "这是测试模式下的模拟结果。请配置正确的LLM提供商（OpenAI、Anthropic或AWS Bedrock）以获取真实的解读。",
            "## 模拟解读\n\n由于未能连接到LLM服务，系统正在使用模拟数据。请检查API密钥设置或网络连接，然后重试。"
        ]
        
        response = random.choice(responses)
        metadata = {
            "mock": True,
            "model": "mock-model",
            "finish_reason": "mock_completion"
        }
        
        return response, metadata
