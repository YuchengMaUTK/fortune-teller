"""
Plugins module for the Fortune Teller application.
Provides access to the fortune telling plugins.
"""
import os
import importlib
import logging
from typing import Dict, List, Any, Type
from pathlib import Path

from fortune_teller.core import BaseFortuneSystem

# Configure logging
logger = logging.getLogger("Plugins")

# Dictionary to store plugin references
plugin_registry = {}

def register_plugin(name: str, plugin_class: Type[BaseFortuneSystem]) -> None:
    """
    Register a plugin with the plugin registry.
    
    Args:
        name: Name of the plugin
        plugin_class: Plugin class that implements BaseFortuneSystem
    """
    if name in plugin_registry:
        logger.warning(f"Plugin {name} is already registered. Overwriting.")
    
    plugin_registry[name] = plugin_class
    logger.debug(f"Registered plugin: {name}")

def get_plugin_class(name: str) -> Type[BaseFortuneSystem]:
    """
    Get a plugin class by name.
    
    Args:
        name: Name of the plugin
        
    Returns:
        Plugin class
        
    Raises:
        KeyError: If plugin is not registered
    """
    if name not in plugin_registry:
        raise KeyError(f"Plugin {name} is not registered")
    
    return plugin_registry[name]

def get_all_plugins() -> Dict[str, Type[BaseFortuneSystem]]:
    """
    Get all registered plugins.
    
    Returns:
        Dictionary mapping plugin names to plugin classes
    """
    return plugin_registry.copy()
