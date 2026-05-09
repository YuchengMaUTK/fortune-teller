"""
MCP Tools Integration for Fortune Teller

Wraps the CLI tools under mcp/tools/ (bazi_converter, tarot_picker,
zodiac_converter) as subprocess calls. Named "MCP" historically; these
are plain Python CLIs, not real MCP-protocol servers.
"""

import subprocess
import json
import os
import sys
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Repository root: fortune_teller/tools/mcp_tools.py -> ../../
_TOOLS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "mcp", "tools")
)


def _run_cli(script: str, args: List[str], timeout: int = 10) -> Dict[str, Any]:
    """Invoke a CLI tool under mcp/tools/ and parse its JSON output."""
    path = os.path.join(_TOOLS_DIR, script)
    if not os.path.exists(path):
        return {"success": False, "error": f"tool not found: {path}"}

    try:
        result = subprocess.run(
            [sys.executable, path, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return {"success": False, "error": f"tool timed out: {e}"}
    except Exception as e:
        logger.error(f"MCP tool {script} exception: {e}")
        return {"success": False, "error": str(e)}

    if result.returncode != 0:
        logger.error(f"MCP tool {script} error: {result.stderr}")
        return {"success": False, "error": result.stderr.strip()}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"invalid JSON from {script}: {e}"}


class MCPTool:
    """Unified dispatcher used by simple_main.

    Usage:
        await MCPTool().invoke_tool("bazi_converter", "convert", [1990, 1, 15, 14])
    """

    # Map logical tool name to CLI script file.
    _SCRIPTS = {
        "bazi_converter": "bazi_converter.py",
        "tarot_converter": "tarot_picker.py",
        "tarot_picker": "tarot_picker.py",
        "zodiac_converter": "zodiac_converter.py",
    }

    # Map simple_main's method names to the CLI subcommand.
    _METHOD_ALIASES = {
        ("tarot_converter", "draw_cards"): "draw",
    }

    async def invoke_tool(
        self, tool_name: str, method: str, args: List[Any]
    ) -> Dict[str, Any]:
        script = self._SCRIPTS.get(tool_name)
        if not script:
            return {"success": False, "error": f"unknown tool: {tool_name}"}

        subcommand = self._METHOD_ALIASES.get((tool_name, method), method)
        cli_args = [subcommand, *[str(a) for a in args]]

        result = _run_cli(script, cli_args)

        # simple_main reads `elements` for BaZi; the CLI returns
        # `five_elements`. Expose both keys so existing prompts work.
        if tool_name == "bazi_converter" and "five_elements" in result:
            result.setdefault("elements", result["five_elements"])

        return result


class MCPTarotTool:
    """Legacy tarot wrapper (kept for backward compatibility)."""

    async def draw_cards(
        self, count: int = 1, allow_reversed: bool = True
    ) -> Dict[str, Any]:
        logger.info(f"[MCP] Tarot draw: count={count} reversed={allow_reversed}")
        return _run_cli(
            "tarot_picker.py", ["draw", str(count), str(allow_reversed).lower()]
        )

    async def get_deck_info(self) -> Dict[str, Any]:
        return _run_cli("tarot_picker.py", ["info"])


class MCPBaZiTool:
    """Legacy BaZi wrapper (kept for backward compatibility)."""

    async def convert_to_bazi(
        self, year: int, month: int, day: int, hour: int = 12
    ) -> Dict[str, Any]:
        logger.info(f"[MCP] BaZi convert: {year}-{month:02d}-{day:02d} {hour:02d}:00")
        return _run_cli(
            "bazi_converter.py",
            ["convert", str(year), str(month), str(day), str(hour)],
        )

    async def get_system_info(self) -> Dict[str, Any]:
        return _run_cli("bazi_converter.py", ["info"])


class MCPZodiacTool:
    """Zodiac wrapper (new; the previous codebase was missing one)."""

    async def convert_to_zodiac(
        self, year: int, month: int, day: int
    ) -> Dict[str, Any]:
        logger.info(f"[MCP] Zodiac convert: {year}-{month:02d}-{day:02d}")
        return _run_cli(
            "zodiac_converter.py", ["convert", str(year), str(month), str(day)]
        )
