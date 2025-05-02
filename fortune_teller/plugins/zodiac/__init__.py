"""
Zodiac/Astrology plugin initialization.
This module registers the Zodiac fortune system with the plugin registry.
"""
from fortune_teller.plugins import register_plugin
from .fortune_system import ZodiacFortuneSystem

# Register the Zodiac fortune system
register_plugin("zodiac", ZodiacFortuneSystem)
