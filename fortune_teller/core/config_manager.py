"""
Configuration manager for fortune telling systems.
Handles loading, saving, and accessing configuration.
"""
import os
import json
import yaml
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ConfigManager")


class ConfigManager:
    """
    Manager for configuration settings.
    Handles loading, saving, and accessing configuration for the application and plugins.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file. If None, uses the default.
        """
        # Default config file location
        if config_file is None:
            self.config_file = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "config.yaml")
            )
        else:
            self.config_file = os.path.abspath(config_file)
        
        # Load or create default configuration
        self.config = self._load_config()
        
        logger.info(f"Configuration manager initialized with config file: {self.config_file}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default configuration.
        
        Returns:
            Configuration dictionary
        """
        try:
            # Check if config file exists
            if os.path.isfile(self.config_file):
                # Determine file format based on extension
                if self.config_file.endswith((".yaml", ".yml")):
                    with open(self.config_file, "r", encoding="utf-8") as f:
                        config = yaml.safe_load(f)
                elif self.config_file.endswith(".json"):
                    with open(self.config_file, "r", encoding="utf-8") as f:
                        config = json.load(f)
                else:
                    logger.warning(f"Unsupported config file format: {self.config_file}")
                    config = self._get_default_config()
                
                logger.info(f"Configuration loaded from {self.config_file}")
                return config or self._get_default_config()
            else:
                logger.info("No configuration file found, creating default configuration")
                config = self._get_default_config()
                self.save_config()
                return config
        
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "app": {
                "name": "Fortune Teller",
                "version": "0.1.0",
                "debug": False
            },
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "plugins": {
                "enabled": ["bazi", "tarot", "zodiac"],
                "bazi": {
                    "data_dir": "data/bazi"
                },
                "tarot": {
                    "data_dir": "data/tarot"
                },
                "zodiac": {
                    "data_dir": "data/zodiac"
                }
            }
        }
    
    def save_config(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Save according to file format
            if self.config_file.endswith((".yaml", ".yml")):
                with open(self.config_file, "w", encoding="utf-8") as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif self.config_file.endswith(".json"):
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=4)
            else:
                logger.warning(f"Unsupported config file format: {self.config_file}")
                return False
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration or a section of the configuration.
        
        Args:
            section: Section of the configuration to get, or None for the entire config
            
        Returns:
            Configuration dictionary or section
        """
        if section is None:
            return self.config
        else:
            return self.config.get(section, {})
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a value from the configuration using a dot notation key path.
        
        Args:
            key_path: Key path in dot notation (e.g., "llm.provider")
            default: Default value to return if key is not found
            
        Returns:
            Value from the configuration or default
        """
        parts = key_path.split(".")
        config = self.config
        
        try:
            # Navigate through the nested dictionary
            for part in parts:
                config = config[part]
            return config
        except (KeyError, TypeError):
            return default
    
    def set_value(self, key_path: str, value: Any) -> None:
        """
        Set a value in the configuration using a dot notation key path.
        
        Args:
            key_path: Key path in dot notation (e.g., "llm.provider")
            value: Value to set
        """
        parts = key_path.split(".")
        config = self.config
        
        # Navigate to the correct level
        for i, part in enumerate(parts[:-1]):
            if part not in config or not isinstance(config[part], dict):
                config[part] = {}
            config = config[part]
        
        # Set the value
        config[parts[-1]] = value
        
        logger.debug(f"Config value set: {key_path} = {value}")
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin-specific configuration
        """
        plugins_config = self.config.get("plugins", {})
        return plugins_config.get(plugin_name, {})
    
    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """
        Check if a plugin is enabled.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if enabled, False otherwise
        """
        plugins_config = self.config.get("plugins", {})
        enabled_plugins = plugins_config.get("enabled", [])
        return plugin_name in enabled_plugins
