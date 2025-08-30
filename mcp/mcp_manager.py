"""
MCP Manager - Centralized MCP tool management
"""

import subprocess
import json
import os
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPManager:
    """Centralized MCP tool manager"""
    
    def __init__(self):
        self.mcp_root = Path(__file__).parent
        self.tools_dir = self.mcp_root / "tools"
        self.servers_dir = self.mcp_root / "servers"
        
        # Registry of available MCP tools
        self.tools_registry = {
            "tarot_picker": {
                "path": self.tools_dir / "tarot_picker.py",
                "description": "High-quality random tarot card picker",
                "commands": ["draw", "info"]
            },
            "bazi_converter": {
                "path": self.tools_dir / "bazi_converter.py", 
                "description": "BaZi Four Pillars calculator",
                "commands": ["convert", "info"]
            },
            "zodiac_converter": {
                "path": self.tools_dir / "zodiac_converter.py",
                "description": "Western zodiac sign calculator", 
                "commands": ["convert", "info"]
            }
        }
    
    async def invoke_tool(self, tool_name: str, command: str, args: List[str] = None, timeout: int = 10) -> Dict[str, Any]:
        """Invoke an MCP tool with proper error handling and logging"""
        if tool_name not in self.tools_registry:
            return {"success": False, "error": f"Unknown MCP tool: {tool_name}"}
        
        tool_info = self.tools_registry[tool_name]
        tool_path = tool_info["path"]
        
        if not tool_path.exists():
            return {"success": False, "error": f"MCP tool not found: {tool_path}"}
        
        if command not in tool_info["commands"]:
            return {"success": False, "error": f"Unknown command '{command}' for tool '{tool_name}'"}
        
        try:
            # Build command
            cmd = ["python", str(tool_path), command]
            if args:
                cmd.extend(args)
            
            print(f"🔧 [MCP] Invoking {tool_name}: {command} {' '.join(args or [])}")
            
            # Execute with timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get("success", True):
                    print(f"✅ [MCP] {tool_name} executed successfully")
                    self._log_tool_result(tool_name, command, response)
                else:
                    print(f"❌ [MCP] {tool_name} failed: {response.get('error', 'Unknown error')}")
                return response
            else:
                error_msg = result.stderr or "Unknown error"
                print(f"❌ [MCP] {tool_name} error: {error_msg}")
                logger.error(f"MCP tool {tool_name} error: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except subprocess.TimeoutExpired:
            error_msg = f"MCP tool {tool_name} timed out after {timeout}s"
            print(f"⏰ [MCP] {error_msg}")
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from {tool_name}: {e}"
            print(f"❌ [MCP] {error_msg}")
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"MCP tool {tool_name} exception: {e}"
            print(f"❌ [MCP] {error_msg}")
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _log_tool_result(self, tool_name: str, command: str, response: Dict[str, Any]):
        """Log tool results with specific formatting"""
        if tool_name == "tarot_picker" and command == "draw":
            cards = response.get("cards", [])
            print(f"   📋 Drew {len(cards)} cards:")
            for i, card in enumerate(cards):
                status = "逆位" if card.get("reversed") else "正位"
                print(f"      Card {i+1}: {card.get('name', 'Unknown')} ({status}) {card.get('emoji', '')}")
        
        elif tool_name == "bazi_converter" and command == "convert":
            pillars = response.get("four_pillars", {})
            elements = response.get("five_elements", {})
            day_master = response.get("day_master", "")
            print(f"   📋 Four Pillars: {pillars.get('year', '')} {pillars.get('month', '')} {pillars.get('day', '')} {pillars.get('hour', '')}")
            print(f"   📋 Day Master: {day_master}")
            print(f"   📋 Elements: {elements}")
        
        elif tool_name == "zodiac_converter" and command == "convert":
            zodiac = response.get("zodiac_sign", {})
            birth_info = response.get("birth_info", {})
            print(f"   📋 Zodiac Sign: {zodiac.get('name', '')} {zodiac.get('emoji', '')} ({zodiac.get('english', '')})")
            print(f"   📋 Element: {zodiac.get('element', '')} ({zodiac.get('element_en', '')})")
            print(f"   📋 Age: {birth_info.get('age', 0)} years, {birth_info.get('days_to_birthday', 0)} days to birthday")
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all available MCP tools"""
        return self.tools_registry.copy()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        return self.tools_registry.get(tool_name)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all MCP tools"""
        results = {}
        
        for tool_name in self.tools_registry:
            try:
                result = await self.invoke_tool(tool_name, "info", timeout=5)
                results[tool_name] = {
                    "status": "healthy" if result.get("success") else "unhealthy",
                    "response": result
                }
            except Exception as e:
                results[tool_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results


# Global MCP manager instance
mcp_manager = MCPManager()


# Convenience functions for specific tools
async def draw_tarot_cards(count: int = 1, allow_reversed: bool = True) -> Dict[str, Any]:
    """Draw tarot cards using MCP manager"""
    return await mcp_manager.invoke_tool(
        "tarot_picker", 
        "draw", 
        [str(count), str(allow_reversed).lower()]
    )


async def convert_to_bazi(year: int, month: int, day: int, hour: int = 12) -> Dict[str, Any]:
    """Convert birth date to BaZi using MCP manager"""
    return await mcp_manager.invoke_tool(
        "bazi_converter",
        "convert", 
        [str(year), str(month), str(day), str(hour)]
    )


async def get_tarot_info() -> Dict[str, Any]:
    """Get tarot deck information"""
    return await mcp_manager.invoke_tool("tarot_picker", "info")


async def convert_to_zodiac(year: int, month: int, day: int) -> Dict[str, Any]:
    """Convert birth date to zodiac sign using MCP manager"""
    return await mcp_manager.invoke_tool(
        "zodiac_converter",
        "convert", 
        [str(year), str(month), str(day)]
    )


async def get_zodiac_info() -> Dict[str, Any]:
    """Get zodiac system information"""
    return await mcp_manager.invoke_tool("zodiac_converter", "info")
