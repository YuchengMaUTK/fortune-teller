"""
LLM 工具 - 提供大语言模型服务
"""

from typing import Dict, Any, Optional, List
import logging
from .base_tool import BaseTool
from ..ui.colors import Colors

logger = logging.getLogger(__name__)


class LLMTool(BaseTool):
    """
    LLM 工具类 - 集成现有的 LLM 连接器
    """
    
    def __init__(self):
        super().__init__("llm_tool")
        self.description = "大语言模型服务工具"
        self.llm_connector = None
    
    async def _setup(self) -> None:
        """初始化 LLM 连接器"""
        try:
            from ..core.llm_connector import LLMConnector
            
            # 使用默认配置初始化连接器
            config = {
                "provider": "aws_bedrock",  # 使用 AWS Bedrock
                "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            self.llm_connector = LLMConnector(config)
            self.logger.info("LLM connector initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM connector: {e}")
            self.llm_connector = None
    
    async def generate_response(self, 
                              system_prompt: str, 
                              user_prompt: str, 
                              language: str = "zh",
                              provider: str = "auto",
                              stream: bool = False,
                              **kwargs) -> str:
        """生成 LLM 响应，支持流式输出"""
        
        if not self.llm_connector:
            self.logger.warning("LLM connector not available, using fallback")
            return f"LLM服务暂时不可用，请稍后重试。"
        
        try:
            if stream:
                return await self._generate_streaming_response(system_prompt, user_prompt)
            else:
                # 使用现有的 LLM 连接器生成响应
                response, metadata = self.llm_connector.generate_response(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    use_cache=True
                )
                
                self.logger.debug(f"Generated response successfully")
                return response
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return f"生成回复时出现错误，请稍后重试。错误信息：{str(e)}"
    
    async def _generate_streaming_response(self, system_prompt: str, user_prompt: str) -> str:
        """流式生成响应"""
        try:
            print(f"\n{Colors.CYAN}🔮 正在生成解读...{Colors.ENDC}\n")
            
            full_response = ""
            
            # 使用连接器的流式方法
            for chunk in self.llm_connector.generate_response_streaming(system_prompt, user_prompt):
                full_response += chunk
                print(chunk, end='', flush=True)
            
            print()  # 换行
            return full_response
            
        except Exception as e:
            self.logger.error(f"Streaming generation failed: {e}")
            # 降级到常规生成
            response, metadata = self.llm_connector.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                use_cache=True
            )
            return response
