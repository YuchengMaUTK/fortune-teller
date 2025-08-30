#!/usr/bin/env python3
"""
Test BaZi agent with streaming output
"""

import asyncio
import sys
import os
import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fortune_teller.agents.bazi_agent import BaZiAgent
from fortune_teller.agents.base_agent import FortuneMessage

async def test_bazi_streaming():
    """Test BaZi agent with streaming"""
    
    print("🀄 Testing BaZi Agent with Streaming Output")
    print("=" * 60)
    
    # Create BaZi agent
    agent = BaZiAgent()
    
    # Create test message
    message = FortuneMessage(
        type="fortune_request",
        sender="user",
        recipient="bazi_agent", 
        session_id="test_session",
        language="zh",
        payload={
            "birth_date": datetime.date(1990, 7, 25),
            "birth_time": datetime.time(14, 30),
            "gender": "男",
            "location": "中国"
        }
    )
    
    print("📋 Test Data:")
    print(f"   出生日期: 1990-07-25")
    print(f"   出生时间: 14:30") 
    print(f"   性别: 男")
    print()
    
    print("🔮 Generating BaZi reading with streaming...")
    print("📝 Watch for text appearing word by word:")
    print("=" * 60)
    
    try:
        # Process the message (should trigger streaming)
        response = await agent.process_message(message)
        
        print("\n" + "=" * 60)
        print("✅ Streaming test completed!")
        print(f"📊 Response type: {response.type}")
        
        if hasattr(response, 'payload') and 'reading' in response.payload:
            reading_length = len(response.payload['reading'])
            print(f"📊 Reading length: {reading_length} characters")
        
    except Exception as e:
        print(f"\n❌ Error during streaming test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bazi_streaming())
