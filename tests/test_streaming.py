#!/usr/bin/env python3
"""
Test streaming output directly
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fortune_teller.tools.llm_tool import LLMTool
from fortune_teller.core.config_manager import ConfigManager

async def test_streaming():
    """Test streaming LLM output"""
    
    print("🔮 Testing Streaming Output...")
    print("=" * 50)
    
    # Initialize LLM tool
    llm_tool = LLMTool()
    
    # Test prompt
    system_prompt = "你是一位经验丰富的八字命理师，精通传统命理学。"
    user_prompt = """
请为以下八字信息提供简短的命理分析：

八字：庚午 甲申 癸丑 己未
日主：癸水
五行：木1 火1 土3 金2 水1

请提供性格特点和运势建议。
"""
    
    print("🎯 Generating reading with streaming...")
    print("📝 You should see text appear word by word:\n")
    
    try:
        # Test streaming output
        result = await llm_tool.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            language="zh",
            stream=True  # Enable streaming
        )
        
        print(f"\n\n✅ Streaming completed!")
        print(f"📊 Total response length: {len(result)} characters")
        
    except Exception as e:
        print(f"❌ Error during streaming: {e}")
        
        # Fallback to non-streaming
        print("\n🔄 Trying non-streaming mode...")
        result = await llm_tool.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            language="zh",
            stream=False
        )
        print(result)

if __name__ == "__main__":
    asyncio.run(test_streaming())
