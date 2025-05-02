"""
Tarot card plugin initialization.
This module registers the Tarot fortune system with the plugin registry.
"""
from fortune_teller.plugins import register_plugin
from .fortune_system import TarotFortuneSystem

# Register the Tarot fortune system
register_plugin("tarot", TarotFortuneSystem)
