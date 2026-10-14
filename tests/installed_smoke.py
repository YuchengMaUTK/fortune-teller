"""Run with a wheel-only environment from outside the checkout."""
import asyncio
import json
import subprocess
import sys
from importlib.resources import files

from fortune_teller.core.plugin_manager import PluginManager
from fortune_teller.i18n import get_available_languages, t
from fortune_teller.tools.mcp_tools import MCPTool

assert set(get_available_languages()) == {"zh", "en"}
assert t("welcome_title", "zh") != "welcome_title"
plugins = PluginManager()
assert set(plugins.discover_plugins()) == {"bazi", "tarot", "zodiac"}
assert plugins.load_all_plugins() == 3
assert json.loads(files("fortune_teller").joinpath("data/tarot/cards.json").read_text())

async def check_tools():
    tools = MCPTool()
    for name, method, args in [
        ("bazi_converter", "convert", [2000, 1, 7, 12]),
        ("tarot_picker", "draw", [3, False]),
        ("zodiac_converter", "convert", [2000, 1, 7]),
    ]:
        result = await tools.invoke_tool(name, method, args)
        assert result["success"], result
    chart = await tools.invoke_tool("bazi_converter", "convert", [2000, 1, 7, 12])
    assert chart["four_pillars"]["day"] == "甲子"

asyncio.run(check_tools())
subprocess.run([sys.executable, "-m", "fortune_teller", "--help"], check=True)
print("Installed wheel smoke check passed")
