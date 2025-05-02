"""
BaZi (Eight Characters) plugin initialization.
This module registers the BaZi fortune system with the plugin registry.
"""
from fortune_teller.plugins import register_plugin
from .fortune_system import BaziFortuneSystem

# Register the BaZi fortune system
register_plugin("bazi", BaziFortuneSystem)
