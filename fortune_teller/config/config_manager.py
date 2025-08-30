"""
配置管理器 - 统一的配置加载和管理
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    配置管理器
    
    提供分层配置管理功能：
    - 系统配置
    - 智能体配置
    - 工具配置
    - 环境配置
    """
    
    def __init__(self, config_root: Optional[str] = None):
        self.config_root = Path(config_root) if config_root else Path(__file__).parent / "files"
        self.configs = {}
        self.watchers = {}
        self.environment = os.getenv("FORTUNE_ENV", "development")
    
    async def initialize(self) -> None:
        """初始化配置管理器"""
        logger.info(f"Initializing config manager with root: {self.config_root}")
        logger.info(f"Environment: {self.environment}")
        
        # 确保配置目录存在
        self.config_root.mkdir(parents=True, exist_ok=True)
        
        # 加载所有配置
        await self._load_all_configs()
    
    async def _load_all_configs(self) -> None:
        """加载所有配置文件"""
        config_files = [
            "system.yaml",
            "strands_config.yaml",
            f"deployment/{self.environment}.yaml"
        ]
        
        for config_file in config_files:
            await self.load_config(config_file)
        
        # 加载智能体配置
        agents_dir = self.config_root / "agents"
        if agents_dir.exists():
            for agent_config in agents_dir.glob("*.yaml"):
                await self.load_config(f"agents/{agent_config.name}")
        
        # 加载工具配置
        tools_dir = self.config_root / "tools"
        if tools_dir.exists():
            for tool_config in tools_dir.glob("*.yaml"):
                await self.load_config(f"tools/{tool_config.name}")
    
    async def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径（相对于配置根目录）
            
        Returns:
            配置数据
        """
        full_path = self.config_root / config_path
        
        if not full_path.exists():
            logger.warning(f"Config file not found: {full_path}")
            return {}
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                if full_path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                elif full_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    logger.error(f"Unsupported config file format: {full_path}")
                    return {}
            
            self.configs[config_path] = config_data or {}
            logger.debug(f"Loaded config: {config_path}")
            return self.configs[config_path]
            
        except Exception as e:
            logger.error(f"Error loading config {config_path}: {e}")
            return {}
    
    def get_config(self, config_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            config_path: 配置路径，支持点号分隔的嵌套路径
            default: 默认值
            
        Returns:
            配置值
        """
        parts = config_path.split('.')
        config_file = parts[0]
        
        if config_file not in self.configs:
            return default
        
        current = self.configs[config_file]
        
        for part in parts[1:]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        获取智能体配置
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            智能体配置
        """
        config_key = f"agents/{agent_name}.yaml"
        return self.configs.get(config_key, {})
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """
        获取工具配置
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具配置
        """
        config_key = f"tools/{tool_name}.yaml"
        return self.configs.get(config_key, {})
    
    def get_strands_config(self) -> Dict[str, Any]:
        """
        获取 Strands Agents 配置
        
        Returns:
            Strands 配置
        """
        return self.configs.get("strands_config.yaml", {})
    
    def get_system_config(self) -> Dict[str, Any]:
        """
        获取系统配置
        
        Returns:
            系统配置
        """
        return self.configs.get("system.yaml", {})
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """
        获取部署配置
        
        Returns:
            部署配置
        """
        return self.configs.get(f"deployment/{self.environment}.yaml", {})
    
    async def reload_config(self, config_path: str) -> Dict[str, Any]:
        """
        重新加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            重新加载的配置数据
        """
        logger.info(f"Reloading config: {config_path}")
        return await self.load_config(config_path)
    
    async def watch_config(self, config_path: str, callback) -> None:
        """
        监控配置文件变化
        
        Args:
            config_path: 配置文件路径
            callback: 变化回调函数
        """
        # TODO: 实现文件监控
        self.watchers[config_path] = callback
        logger.info(f"Watching config: {config_path}")
    
    def list_configs(self) -> List[str]:
        """
        列出所有已加载的配置
        
        Returns:
            配置文件列表
        """
        return list(self.configs.keys())