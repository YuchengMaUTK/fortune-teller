"""
Fortune Teller - Multi-system Fortune Telling Application

A Python-based application for fortune telling using various systems,
powered by large language models for interpretation.
"""

__version__ = '0.1.0'

# Import main components for easier access
from fortune_teller.core import (
    BaseFortuneSystem,
    PluginManager, 
    LLMConnector, 
    ConfigManager
)

# Import main application class
from fortune_teller.main import FortuneTeller, main
