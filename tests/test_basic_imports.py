"""
Basic import tests to verify the package structure is correct.
"""
import pytest

def test_core_imports():
    """Test that core modules can be imported."""
    from fortune_teller.core import BaseFortuneSystem
    from fortune_teller.core import ConfigManager
    from fortune_teller.core import LLMConnector
    from fortune_teller.core import PluginManager
    
    assert BaseFortuneSystem is not None
    assert ConfigManager is not None
    assert LLMConnector is not None
    assert PluginManager is not None

def test_plugin_imports():
    """Test that plugin modules can be imported."""
    import fortune_teller.plugins
    
    # Just check that the plugins package exists
    assert fortune_teller.plugins is not None

def test_utils_imports():
    """Test that utility modules can be imported."""
    import fortune_teller.utils
    
    # Just check that the utils package exists
    assert fortune_teller.utils is not None

def test_ui_imports():
    """Test that UI modules can be imported."""
    import fortune_teller.ui
    from fortune_teller.ui import colors
    
    assert fortune_teller.ui is not None
    assert colors is not None
