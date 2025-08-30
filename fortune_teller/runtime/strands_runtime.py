"""
Strands Agents 运行时环境
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..config import ConfigManager, StrandsConfig
from ..agents import BaseFortuneAgent, MasterAgent
from ..agents.bazi_agent import BaZiAgent
from ..agents.tarot_agent import TarotAgent
from ..agents.zodiac_agent import ZodiacAgent
from ..agents.chat_agent import ChatAgent
from ..agents.i18n_agent import I18nAgent
from ..tools import BaseTool, LLMTool, DateTool
from .message_bus import MessageBus
from .state_manager import StateManager

logger = logging.getLogger(__name__)


class StrandsRuntime:
    """
    Strands Agents 运行时环境
    
    负责：
    - 智能体生命周期管理
    - 工具注册和管理
    - 消息路由和传递
    - 状态管理
    - 配置管理
    """
    
    def __init__(self, config_root: Optional[str] = None):
        self.config_manager = ConfigManager(config_root)
        self.strands_config = None
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        
        # 注册表
        self.agents: Dict[str, BaseFortuneAgent] = {}
        self.tools: Dict[str, BaseTool] = {}
        self.agent_classes: Dict[str, type] = {}
        self.tool_classes: Dict[str, type] = {}
        
        # 运行状态
        self.running = False
        self.initialized = False
        
        # 注册内置类
        self._register_builtin_classes()
    
    def _register_builtin_classes(self):
        """注册内置的智能体和工具类"""
        # 注册智能体类
        self.agent_classes.update({
            "MasterAgent": MasterAgent,
            "BaZiAgent": BaZiAgent,
            "TarotAgent": TarotAgent,
            "ZodiacAgent": ZodiacAgent,
            "ChatAgent": ChatAgent,
            "I18nAgent": I18nAgent,
            # TODO: 添加其他智能体类
            # "ZodiacAgent": ZodiacAgent,
            # "ChatAgent": ChatAgent,
            # "I18nAgent": I18nAgent,
            # "AdminAgent": AdminAgent,
        })
        
        # 注册工具类
        self.tool_classes.update({
            "LLMTool": LLMTool,
            "DateTool": DateTool,
            # TODO: 添加其他工具类
            # "TarotDataTool": TarotDataTool,
            # "ZodiacDataTool": ZodiacDataTool,
        })
    
    async def initialize(self) -> None:
        """初始化运行时环境"""
        if self.initialized:
            logger.warning("Runtime already initialized")
            return
        
        logger.info("Initializing Strands runtime")
        
        # 初始化配置管理器
        await self.config_manager.initialize()
        
        # 加载 Strands 配置
        strands_config_data = self.config_manager.get_strands_config()
        self.strands_config = StrandsConfig(strands_config_data)
        
        # 初始化消息总线
        await self.message_bus.initialize()
        
        # 初始化状态管理器
        await self.state_manager.initialize()
        
        # 初始化工具
        await self._initialize_tools()
        
        # 初始化智能体
        await self._initialize_agents()
        
        self.initialized = True
        logger.info("Strands runtime initialized successfully")
    
    async def start(self) -> None:
        """启动运行时环境"""
        if not self.initialized:
            await self.initialize()
        
        if self.running:
            logger.warning("Runtime already running")
            return
        
        logger.info("Starting Strands runtime")
        
        # 启动消息总线
        await self.message_bus.start()
        
        # 启动状态管理器
        await self.state_manager.start()
        
        # 启动自动启动的智能体
        await self._start_auto_start_agents()
        
        self.running = True
        logger.info("Strands runtime started successfully")
    
    async def stop(self) -> None:
        """停止运行时环境"""
        if not self.running:
            logger.warning("Runtime not running")
            return
        
        logger.info("Stopping Strands runtime")
        
        # 停止所有智能体
        await self._stop_all_agents()
        
        # 停止所有工具
        await self._stop_all_tools()
        
        # 停止状态管理器
        await self.state_manager.stop()
        
        # 停止消息总线
        await self.message_bus.stop()
        
        self.running = False
        logger.info("Strands runtime stopped successfully")
    
    async def _initialize_tools(self) -> None:
        """初始化工具"""
        logger.info("Initializing tools")
        
        for tool_config in self.strands_config.tools:
            await self._create_tool(tool_config)
        
        logger.info(f"Initialized {len(self.tools)} tools")
    
    async def _initialize_agents(self) -> None:
        """初始化智能体"""
        logger.info("Initializing agents")
        
        for agent_config in self.strands_config.agents:
            await self._create_agent(agent_config)
        
        logger.info(f"Initialized {len(self.agents)} agents")
    
    async def _create_tool(self, tool_config) -> None:
        """创建工具实例"""
        tool_class = self.tool_classes.get(tool_config.class_name)
        if not tool_class:
            logger.error(f"Unknown tool class: {tool_config.class_name}")
            return
        
        try:
            tool = tool_class()
            await tool.initialize()
            self.tools[tool_config.name] = tool
            logger.debug(f"Created tool: {tool_config.name}")
        except Exception as e:
            logger.error(f"Failed to create tool {tool_config.name}: {e}")
    
    async def _create_agent(self, agent_config) -> None:
        """创建智能体实例"""
        agent_class = self.agent_classes.get(agent_config.class_name)
        if not agent_class:
            logger.error(f"Unknown agent class: {agent_config.class_name}")
            return
        
        try:
            agent = agent_class(agent_config.name, agent_config.config)
            await agent.initialize()
            
            # 注入运行时引用
            if hasattr(agent, 'set_runtime'):
                await agent.set_runtime(self)
            
            self.agents[agent_config.name] = agent
            logger.debug(f"Created agent: {agent_config.name}")
        except Exception as e:
            logger.error(f"Failed to create agent {agent_config.name}: {e}")
    
    async def _start_auto_start_agents(self) -> None:
        """启动自动启动的智能体"""
        for agent_config in self.strands_config.agents:
            if agent_config.auto_start and agent_config.name in self.agents:
                agent = self.agents[agent_config.name]
                try:
                    await agent.start()
                    logger.debug(f"Auto-started agent: {agent_config.name}")
                except Exception as e:
                    logger.error(f"Failed to start agent {agent_config.name}: {e}")
    
    async def _stop_all_agents(self) -> None:
        """停止所有智能体"""
        for agent_name, agent in self.agents.items():
            try:
                await agent.shutdown()
                logger.debug(f"Stopped agent: {agent_name}")
            except Exception as e:
                logger.error(f"Error stopping agent {agent_name}: {e}")
    
    async def _stop_all_tools(self) -> None:
        """停止所有工具"""
        for tool_name, tool in self.tools.items():
            try:
                await tool.shutdown()
                logger.debug(f"Stopped tool: {tool_name}")
            except Exception as e:
                logger.error(f"Error stopping tool {tool_name}: {e}")
    
    def get_agent(self, agent_name: str) -> Optional[BaseFortuneAgent]:
        """
        获取智能体实例
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            智能体实例，如果不存在则返回 None
        """
        return self.agents.get(agent_name)
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取工具实例
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例，如果不存在则返回 None
        """
        return self.tools.get(tool_name)
    
    def list_agents(self) -> List[str]:
        """
        列出所有智能体名称
        
        Returns:
            智能体名称列表
        """
        return list(self.agents.keys())
    
    def list_tools(self) -> List[str]:
        """
        列出所有工具名称
        
        Returns:
            工具名称列表
        """
        return list(self.tools.keys())
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取运行时状态
        
        Returns:
            运行时状态信息
        """
        agent_status = {}
        for name, agent in self.agents.items():
            agent_status[name] = agent.get_status()
        
        tool_status = {}
        for name, tool in self.tools.items():
            tool_status[name] = tool.get_info()
        
        return {
            "runtime": {
                "initialized": self.initialized,
                "running": self.running,
                "agent_count": len(self.agents),
                "tool_count": len(self.tools)
            },
            "agents": agent_status,
            "tools": tool_status,
            "message_bus": self.message_bus.get_status(),
            "state_manager": self.state_manager.get_status()
        }