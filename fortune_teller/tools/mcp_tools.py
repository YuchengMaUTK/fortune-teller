"""
MCP Tools Integration for Fortune Teller
"""

import subprocess
import json
import os
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MCPTarotTool:
    """MCP Tarot Card Picker Tool"""
    
    def __init__(self):
        self.tool_path = os.path.join(os.path.dirname(__file__), "../../mcp_tools/tarot_picker.py")
    
    async def draw_cards(self, count: int = 1, allow_reversed: bool = True) -> Dict[str, Any]:
        """Draw tarot cards using MCP tool"""
        try:
            print(f"🔧 [MCP] Invoking Tarot Picker: drawing {count} cards...")
            
            cmd = ["python", self.tool_path, "draw", str(count), str(allow_reversed).lower()]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get("success"):
                    cards = response.get("cards", [])
                    print(f"✅ [MCP] Tarot cards drawn successfully: {len(cards)} cards")
                    for i, card in enumerate(cards):
                        status = "逆位" if card.get("reversed") else "正位"
                        print(f"   📋 Card {i+1}: {card.get('name', 'Unknown')} ({status}) {card.get('emoji', '')}")
                else:
                    print(f"❌ [MCP] Tarot tool failed: {response.get('error', 'Unknown error')}")
                return response
            else:
                print(f"❌ [MCP] Tarot tool error: {result.stderr}")
                logger.error(f"MCP Tarot tool error: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            print(f"❌ [MCP] Tarot tool exception: {e}")
            logger.error(f"MCP Tarot tool exception: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_deck_info(self) -> Dict[str, Any]:
        """Get tarot deck information"""
        try:
            cmd = ["python", self.tool_path, "info"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


class MCPBaZiTool:
    """MCP BaZi Time Converter Tool"""
    
    def __init__(self):
        self.tool_path = os.path.join(os.path.dirname(__file__), "../../mcp_tools/bazi_converter.py")
    
    async def convert_to_bazi(self, year: int, month: int, day: int, hour: int = 12) -> Dict[str, Any]:
        """Convert birth date/time to BaZi Four Pillars"""
        try:
            print(f"🔧 [MCP] Invoking BaZi Converter: {year}-{month:02d}-{day:02d} {hour:02d}:00...")
            
            cmd = ["python", self.tool_path, "convert", str(year), str(month), str(day), str(hour)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get("success"):
                    pillars = response.get("four_pillars", {})
                    elements = response.get("five_elements", {})
                    day_master = response.get("day_master", "")
                    print(f"✅ [MCP] BaZi calculated successfully:")
                    print(f"   📋 Four Pillars: {pillars.get('year', '')} {pillars.get('month', '')} {pillars.get('day', '')} {pillars.get('hour', '')}")
                    print(f"   📋 Day Master: {day_master}")
                    print(f"   📋 Elements: {elements}")
                else:
                    print(f"❌ [MCP] BaZi tool failed: {response.get('error', 'Unknown error')}")
                return response
            else:
                print(f"❌ [MCP] BaZi tool error: {result.stderr}")
                logger.error(f"MCP BaZi tool error: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            print(f"❌ [MCP] BaZi tool exception: {e}")
            logger.error(f"MCP BaZi tool exception: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get BaZi system information"""
        try:
            cmd = ["python", self.tool_path, "info"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
