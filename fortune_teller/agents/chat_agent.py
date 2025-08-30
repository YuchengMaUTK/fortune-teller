"""
聊天智能体 - 完整实现
"""

from .base_agent import BaseFortuneAgent, FortuneMessage, MessagePriority
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ChatAgent(BaseFortuneAgent):
    """聊天智能体 - 提供基于占卜结果的深度对话"""
    
    def __init__(self, agent_name: str = "chat_agent", config: Dict[str, Any] = None):
        super().__init__(agent_name, config)
        self.system_name = "chat"
        self.display_name = "霄占聊天"
        self.description = "与霄占命理师进行深度对话"
        
        # 聊天上下文存储
        self.chat_contexts = {}  # {session_id: [messages]}
    
    async def validate_input(self, message: FortuneMessage) -> Dict[str, Any]:
        """验证聊天输入"""
        payload = message.payload or {}
        
        # 聊天输入相对简单
        user_message = payload.get("message", "")
        session_id = message.session_id
        previous_reading = payload.get("previous_reading", {})
        
        return {
            "valid": True,
            "system": "chat",
            "user_message": user_message,
            "session_id": session_id,
            "previous_reading": previous_reading
        }
    
    async def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """处理聊天数据 - 管理对话上下文"""
        user_message = validated_input["user_message"]
        session_id = validated_input["session_id"]
        previous_reading = validated_input["previous_reading"]
        
        # 初始化或获取聊天上下文
        if session_id not in self.chat_contexts:
            self.chat_contexts[session_id] = []
        
        chat_context = self.chat_contexts[session_id]
        
        # 添加用户消息到上下文
        chat_context.append(f"用户: {user_message}")
        
        # 保持上下文长度合理（最多10轮对话）
        if len(chat_context) > 20:  # 10轮对话 = 20条消息
            chat_context = chat_context[-20:]
            self.chat_contexts[session_id] = chat_context
        
        return {
            "system": "chat",
            "user_message": user_message,
            "session_id": session_id,
            "chat_context": chat_context,
            "previous_reading": previous_reading
        }
    
    async def generate_reading(self, processed_data: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
        """生成聊天回复"""
        
        user_message = processed_data["user_message"]
        chat_context = processed_data["chat_context"]
        previous_reading = processed_data["previous_reading"]
        session_id = processed_data["session_id"]
        
        # 构建聊天上下文
        context_text = "\n".join(chat_context[-10:]) if chat_context else ""  # 最近5轮对话
        
        # 构建之前的占卜信息
        reading_context = ""
        if previous_reading:
            system = previous_reading.get("system", "")
            reading = previous_reading.get("reading", "")
            if system and reading:
                reading_context = f"\n\n【之前的占卜结果】\n系统: {system}\n解读: {reading[:300]}..."
        
        # 使用 LLM 工具生成回复
        llm_tool = await self.get_tool("llm_tool")
        
        system_prompt = """你是"霄占"命理大师，一位来自中国的命理学专家，已有30年的占卜经验，性格风趣幽默又不失智慧。

现在你正在与求测者进行轻松的聊天互动。你可以谈论命理学知识、回答关于运势的问题，
也可以聊一些日常话题，但始终保持着命理师的角色和视角。

用生动有趣的语言表达，偶尔引用古诗词或俏皮话，让谈话充满趣味性。
让求测者感觉是在和一位睿智而亲切的老朋友聊天。

对话应简洁精炼，回答控制在200字以内，保持幽默风趣的语气。"""

        user_prompt = f"""
{reading_context}

【对话历史】
{context_text}

【当前问题】
用户: {user_message}

请以霄占命理师的身份，用温和风趣的语气回复用户的问题。如果用户询问占卜相关的问题，可以结合之前的占卜结果进行深入解答。
"""
        
        try:
            chat_response = await llm_tool.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                language=language
            )
            
            # 将AI回复添加到聊天上下文
            self.chat_contexts[session_id].append(f"霄占: {chat_response}")
            
            return {
                "system": "chat",
                "response": chat_response,
                "session_id": session_id,
                "timestamp": self.get_current_time()
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            
            # 后备回复
            fallback_responses = [
                "哈哈，这个问题很有趣呢！不过老夫需要再仔细想想，您可以换个角度问问看。",
                "嗯，您这个问题让我想起一句话：'山重水复疑无路，柳暗花明又一村'。有时候答案就在转角处呢！",
                "老夫行走江湖这么多年，您这个问题还真是第一次遇到！不如我们换个话题聊聊？",
                "哎呀，刚才走神了，您能再说一遍吗？老夫这就为您详细解答！"
            ]
            
            import random
            fallback_response = random.choice(fallback_responses)
            
            # 将后备回复也添加到上下文
            self.chat_contexts[session_id].append(f"霄占: {fallback_response}")
            
            return {
                "system": "chat",
                "response": fallback_response,
                "session_id": session_id,
                "timestamp": self.get_current_time()
            }
    
    def clear_chat_context(self, session_id: str):
        """清除聊天上下文"""
        if session_id in self.chat_contexts:
            del self.chat_contexts[session_id]
