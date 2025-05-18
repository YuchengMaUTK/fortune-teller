"""
Mock LLM Connector for fortune telling systems.
Used as a fallback when no real LLM is available.
"""
import logging
import random
import time
from typing import Dict, Any, Tuple, Generator

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
        
        # Get the appropriate mock response
        response = self._get_mock_response(system_name, user_prompt)
        
        metadata = {
            "mock": True,
            "model": "mock-model",
            "finish_reason": "mock_completion",
            "system": system_name
        }
        
        return response, metadata

    def _get_mock_response(self, system_name: str, user_prompt: str) -> str:
        """Get an appropriate mock response based on the system and prompt."""
        
        # Check if this is for a tarot reading
        if system_name == "塔罗牌" and ("三牌阵" in user_prompt or "three_card" in user_prompt):
            return self._generate_mock_tarot_reading()
        
        # Basic mock responses if no specific patterns are detected
        responses = [
            f"这是一个来自{system_name}的模拟解读结果。在实际使用时，这里会显示由LLM生成的专业解读内容。",
            "## 总体运势\n\n这是一个模拟的运势分析，用于测试系统功能。实际使用时，这里将显示基于您输入信息的详细解读。",
            "这是测试模式下的模拟结果。请配置正确的LLM提供商（OpenAI、Anthropic或AWS Bedrock）以获取真实的解读。",
            "## 模拟解读\n\n由于未能连接到LLM服务，系统正在使用模拟数据。请检查API密钥设置或网络连接，然后重试。"
        ]
        
        return random.choice(responses)
    
    def _generate_mock_tarot_reading(self) -> str:
        """Generate a more detailed mock tarot card reading."""
        return """【 整体解读 】

塔罗牌解读：感情三牌阵详细分析

过去牌 - 命运之轮(正位):
在感情领域,这张牌意味着过去经历了重大的转折和变化。可能是一段关系的起起落落,或者是命运中的偶然际遇。这是一个充满动态和可能性的阶段,暗示咨询者经历了情感生活中的重要转折点。过去的经历教会了你接受变化,学会随机应变,并且相信生命中存在某种更高的秩序。

现在牌 - 战车(逆位):
逆位的战车显示目前在感情中可能存在内心的矛盾和行动的阻碍。你可能感到难以前进,缺乏明确的方向,或者在感情中遇到了挫折。内心的犹豫不决阻碍了你追求理想关系的步伐。这可能源于自信的缺失,或者对未来的不确定感。需要重新审视自己的情感状态,梳理内心真正的渴望。

未来牌 - 恋人(正位):
这是一张非常积极的牌面,预示着感情领域即将迎来和谐与平衡。未来很可能会出现一段建立在相互理解和共同价值观基础上的关系。这张牌暗示即将做出重要的情感选择,这个选择将带来更深层次的亲密和连接。

【 各牌位详细解读 】

过去位 - 命运之轮:
命运之轮象征着循环、变化和更替。在过去位置上,它表明你的感情经历了起伏波动的周期。也许是一段旧的关系结束,或者经历了搬迁、工作变动等导致情感生活发生转变的外部事件。这张牌提醒你,过去的这些变化虽然可能带来不适,但都是生命中必要的部分,帮助你成长和学习。

现在位 - 战车逆位:
战车在正位时象征着决心和前进的力量,但在逆位时,这种能量受到阻碍。你目前可能在感情上感到举棋不定,或者面临来自自己或伴侣的不同方向的拉力。这张牌建议你暂时放慢脚步,不要急于做出决定或采取行动。这是一个内省和调整方向的时期,而不是冲刺向前的时刻。

未来位 - 恋人:
恋人牌象征着选择、联合和和谐的关系。在未来位置上,它预示着即将做出与爱情相关的重要选择,而这个选择将带来积极的结果。这可能是一段新关系的开始,或现有关系中的一个新阶段。恋人牌强调的是基于相互尊重和共同价值观的连接,而不仅仅是短暂的吸引。

【 整合建议 】

从命运之轮到战车逆位再到恋人,你的感情线索展现了一个从过去的变动,经过当前的停滞,最终迎来和谐选择的旅程。目前的不确定感或挫折感是暂时的,是为了让你有时间反思真正想要的是什么。

建议:
1. 接受目前感情中的不确定性,视其为一个反思的机会
2. 花时间探索自己真正的情感需求和价值观
3. 不要强迫自己做出决定,顺其自然让情感发展
4. 保持开放的心态,为即将到来的新可能做好准备

记住,塔罗牌提供的是可能性而非绝对的预言,最终如何行动和选择始终掌握在你自己手中。"""

    def generate_response_streaming(self, 
                                   system_prompt: str, 
                                   user_prompt: str) -> Generator[str, None, None]:
        """
        Generate a streaming mock response, simulating chunks being received over time.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            
        Returns:
            Generator yielding text chunks
        """
        logger.warning("Using mock streaming response - this is only for testing!")
        
        # Get the full response first
        full_response, _ = self.generate_response(system_prompt, user_prompt)
        
        # Add a header indicating this is a mock response
        yield "【注意：使用模拟流式输出】\n\n"
        time.sleep(0.2)
        
        # Determine chunking strategy - character by character is good for testing
        chars = list(full_response)
        
        # Options for chunk sizes (how many characters per chunk)
        chunk_size_options = [1, 1, 1, 2, 2, 3, 5]  # Bias toward smaller chunks
        
        position = 0
        while position < len(chars):
            # Random chunk size for more realistic streaming
            chunk_size = min(random.choice(chunk_size_options), len(chars) - position)
            
            # Get the next chunk
            chunk = ''.join(chars[position:position+chunk_size])
            yield chunk
            
            # Move position forward
            position += chunk_size
            
            # Random delay between chunks (50-150ms)
            time.sleep(random.uniform(0.05, 0.15))
