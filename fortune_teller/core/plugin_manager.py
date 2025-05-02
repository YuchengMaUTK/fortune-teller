"""
Plugin manager for fortune telling systems.
Responsible for discovering, loading and managing fortune system plugins.
"""
import os
import importlib
import importlib.util
import yaml
import logging
from typing import Dict, List, Optional, Type
from .base_system import BaseFortuneSystem

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PluginManager")


class PluginManager:
    """
    Manager for fortune system plugins.
    Handles discovery, loading, and access to plugins.
    """
    
    def __init__(self, plugins_dir: str = None):
        """
        Initialize the plugin manager.
        
        Args:
            plugins_dir: Directory containing the plugins. If None, uses the default.
        """
        # Default to the plugins directory in the package
        if plugins_dir is None:
            self.plugins_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "plugins")
            )
        else:
            self.plugins_dir = os.path.abspath(plugins_dir)
        
        # Dictionary to store loaded plugin systems
        self.plugins: Dict[str, BaseFortuneSystem] = {}
        
        logger.info(f"Plugin manager initialized with plugins directory: {self.plugins_dir}")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugins directory.
        
        Returns:
            List of plugin directory names
        """
        plugin_dirs = []
        
        try:
            # List all directories in the plugins directory
            for item in os.listdir(self.plugins_dir):
                item_path = os.path.join(self.plugins_dir, item)
                # Check if it's a directory and contains manifest.yaml
                if (os.path.isdir(item_path) and 
                    os.path.isfile(os.path.join(item_path, "manifest.yaml"))):
                    plugin_dirs.append(item)
            
            logger.info(f"Discovered {len(plugin_dirs)} potential plugins: {plugin_dirs}")
            return plugin_dirs
        
        except Exception as e:
            logger.error(f"Error discovering plugins: {e}")
            return []
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a single plugin by name.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            True if plugin was loaded successfully, False otherwise
        """
        try:
            plugin_dir = os.path.join(self.plugins_dir, plugin_name)
            
            # Check if plugin directory exists
            if not os.path.isdir(plugin_dir):
                logger.error(f"Plugin directory does not exist: {plugin_dir}")
                return False
            
            # Load manifest
            manifest_path = os.path.join(plugin_dir, "manifest.yaml")
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)
            
            # Get the main module and class from manifest
            module_name = manifest.get("module", "fortune_system")
            class_name = manifest.get("class", "FortuneSystem")
            
            # Import the module
            module_path = os.path.join(plugin_dir, f"{module_name}.py")
            spec = importlib.util.spec_from_file_location(
                f"fortune_teller.plugins.{plugin_name}.{module_name}", 
                module_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the class and instantiate it
            plugin_class = getattr(module, class_name)
            plugin_instance = plugin_class()
            
            # Validate that it's a proper plugin
            if not isinstance(plugin_instance, BaseFortuneSystem):
                logger.error(
                    f"Plugin {plugin_name} does not implement BaseFortuneSystem"
                )
                return False
            
            # Add to plugins dictionary
            self.plugins[plugin_name] = plugin_instance
            logger.info(f"Successfully loaded plugin: {plugin_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> int:
        """
        Discover and load all available plugins.
        
        Returns:
            Number of successfully loaded plugins
        """
        plugin_dirs = self.discover_plugins()
        loaded_count = 0
        
        for plugin_name in plugin_dirs:
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        logger.info(f"Successfully loaded {loaded_count} out of {len(plugin_dirs)} plugins")
        return loaded_count
    
    def get_plugin(self, name: str) -> Optional[BaseFortuneSystem]:
        """
        Get a plugin by name.
        
        Args:
            name: Name of the plugin
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, BaseFortuneSystem]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary mapping plugin names to plugin instances
        """
        return self.plugins
    
    def get_plugin_info_list(self) -> List[Dict]:
        """
        Get information about all loaded plugins.
        
        Returns:
            List of plugin info dictionaries
        """
        return [plugin.get_system_info() for plugin in self.plugins.values()]
