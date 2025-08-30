"""
基础工具类 - 所有工具的基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

# TODO: Import from strands-agents when available
# from strands_agents import StrandsTool

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    基础工具类
    
    所有工具都应该继承此类并实现抽象方法。
    提供统一的工具接口和错误处理。
    """
    
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.description = ""
        self.version = "1.0.0"
        self.logger = logging.getLogger(f"tool.{tool_name}")
        self.initialized = False
    
    async def initialize(self) -> None:
        """初始化工具"""
        self.logger.info(f"Initializing tool: {self.tool_name}")
        await self._setup()
        self.initialized = True
    
    async def shutdown(self) -> None:
        """关闭工具"""
        self.logger.info(f"Shutting down tool: {self.tool_name}")
        await self._cleanup()
        self.initialized = False
    
    @abstractmethod
    async def _setup(self) -> None:
        """工具特定的初始化逻辑"""
        pass
    
    async def _cleanup(self) -> None:
        """工具特定的清理逻辑"""
        # 默认实现，子类可以重写
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        return {
            "name": self.tool_name,
            "description": self.description,
            "version": self.version,
            "initialized": self.initialized
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "tool_name": self.tool_name,
            "status": "healthy" if self.initialized else "not_initialized",
            "initialized": self.initialized
        }