"""
Strands Agents 配置类
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """智能体配置"""
    name: str
    class_name: str
    max_instances: int = 1
    auto_start: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolConfig:
    """工具配置"""
    name: str
    class_name: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPToolConfig:
    """MCP 工具配置"""
    name: str
    server: str
    description: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeConfig:
    """运行时配置"""
    name: str = "fortune_teller_system"
    version: str = "2.0.0"
    max_agents: int = 50
    message_timeout: int = 30
    state_persistence: bool = True


class StrandsConfig:
    """
    Strands Agents 配置管理类
    
    负责解析和管理 Strands Agents 的配置信息
    """
    
    def __init__(self, config_data: Dict[str, Any]):
        self.config_data = config_data
        self.runtime = self._parse_runtime_config()
        self.agents = self._parse_agents_config()
        self.tools = self._parse_tools_config()
        self.mcp_tools = self._parse_mcp_tools_config()
    
    def _parse_runtime_config(self) -> RuntimeConfig:
        """解析运行时配置"""
        runtime_data = self.config_data.get("runtime", {})
        return RuntimeConfig(
            name=runtime_data.get("name", "fortune_teller_system"),
            version=runtime_data.get("version", "2.0.0"),
            max_agents=runtime_data.get("max_agents", 50),
            message_timeout=runtime_data.get("message_timeout", 30),
            state_persistence=runtime_data.get("state_persistence", True)
        )
    
    def _parse_agents_config(self) -> List[AgentConfig]:
        """解析智能体配置"""
        agents_data = self.config_data.get("agents", [])
        agents = []
        
        for agent_data in agents_data:
            agent = AgentConfig(
                name=agent_data["name"],
                class_name=agent_data["class"],
                max_instances=agent_data.get("max_instances", 1),
                auto_start=agent_data.get("auto_start", True),
                config=agent_data.get("config", {})
            )
            agents.append(agent)
        
        logger.info(f"Parsed {len(agents)} agent configurations")
        return agents
    
    def _parse_tools_config(self) -> List[ToolConfig]:
        """解析工具配置"""
        tools_data = self.config_data.get("tools", [])
        tools = []
        
        for tool_data in tools_data:
            tool = ToolConfig(
                name=tool_data["name"],
                class_name=tool_data["class"],
                config=tool_data.get("config", {})
            )
            tools.append(tool)
        
        logger.info(f"Parsed {len(tools)} tool configurations")
        return tools
    
    def _parse_mcp_tools_config(self) -> List[MCPToolConfig]:
        """解析 MCP 工具配置"""
        mcp_tools_data = self.config_data.get("mcp_tools", [])
        mcp_tools = []
        
        for mcp_tool_data in mcp_tools_data:
            mcp_tool = MCPToolConfig(
                name=mcp_tool_data["name"],
                server=mcp_tool_data["server"],
                description=mcp_tool_data["description"],
                config=mcp_tool_data.get("config", {})
            )
            mcp_tools.append(mcp_tool)
        
        logger.info(f"Parsed {len(mcp_tools)} MCP tool configurations")
        return mcp_tools
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """
        获取指定智能体的配置
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            智能体配置，如果不存在则返回 None
        """
        for agent in self.agents:
            if agent.name == agent_name:
                return agent
        return None
    
    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """
        获取指定工具的配置
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具配置，如果不存在则返回 None
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_mcp_tool_config(self, mcp_tool_name: str) -> Optional[MCPToolConfig]:
        """
        获取指定 MCP 工具的配置
        
        Args:
            mcp_tool_name: MCP 工具名称
            
        Returns:
            MCP 工具配置，如果不存在则返回 None
        """
        for mcp_tool in self.mcp_tools:
            if mcp_tool.name == mcp_tool_name:
                return mcp_tool
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典格式
        
        Returns:
            配置字典
        """
        return {
            "runtime": {
                "name": self.runtime.name,
                "version": self.runtime.version,
                "max_agents": self.runtime.max_agents,
                "message_timeout": self.runtime.message_timeout,
                "state_persistence": self.runtime.state_persistence
            },
            "agents": [
                {
                    "name": agent.name,
                    "class": agent.class_name,
                    "max_instances": agent.max_instances,
                    "auto_start": agent.auto_start,
                    "config": agent.config
                }
                for agent in self.agents
            ],
            "tools": [
                {
                    "name": tool.name,
                    "class": tool.class_name,
                    "config": tool.config
                }
                for tool in self.tools
            ],
            "mcp_tools": [
                {
                    "name": mcp_tool.name,
                    "server": mcp_tool.server,
                    "description": mcp_tool.description,
                    "config": mcp_tool.config
                }
                for mcp_tool in self.mcp_tools
            ]
        }