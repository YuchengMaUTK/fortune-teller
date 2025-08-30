#!/usr/bin/env python3
"""
Simple streaming test - directly test the LLM streaming
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_streaming():
    """Test streaming output directly"""
    
    print("🔮 Testing Streaming Output")
    print("=" * 40)
    
    # Import after path setup
    from fortune_teller.core.aws_connector import AWSBedrockConnector
    
    try:
        # Create connector
        connector = AWSBedrockConnector()
        
        # Test prompts
        system_prompt = "你是一位经验丰富的八字命理师。请提供简洁的命理分析。"
        user_prompt = """
请为以下信息提供八字命理分析：

出生信息：1990年7月25日 14:30 男性
八字：庚午 甲申 癸丑 己未
日主：癸水

请分析性格特点和运势建议，保持简洁。
"""
        
        print("🎯 Starting streaming generation...")
        print("📝 You should see text appear gradually:\n")
        print("-" * 40)
        
        # Test streaming
        full_response = ""
        for chunk in connector.generate_response_streaming(system_prompt, user_prompt):
            full_response += chunk
            print(chunk, end='', flush=True)
        
        print("\n" + "-" * 40)
        print(f"✅ Streaming completed!")
        print(f"📊 Total length: {len(full_response)} characters")
        
    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        print("🔄 This might be expected if no LLM is configured")

if __name__ == "__main__":
    asyncio.run(test_streaming())
