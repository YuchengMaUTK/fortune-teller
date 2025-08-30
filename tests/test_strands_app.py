#!/usr/bin/env python3
"""
Test the Strands application startup and basic functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fortune_teller.strands_main import FortunetellerStrandsApp


async def test_app_startup():
    """Test application startup and basic functionality"""
    print("🧪 Testing Strands Application Startup...")
    
    try:
        app = FortunetellerStrandsApp()
        
        # Test initialization
        success = await app.initialize()
        if not success:
            print("❌ Application initialization failed")
            return False
        
        print("✅ Application initialized successfully")
        
        # Test runtime status
        runtime_status = app.runtime.get_status()
        print(f"📊 Runtime Status: {runtime_status['runtime']}")
        
        # Test master agent
        master_agent = app.runtime.get_agent("master_agent")
        if master_agent:
            print("✅ Master agent found and accessible")
            
            # Test agent status
            agent_status = master_agent.get_status()
            print(f"🤖 Master Agent Status: {agent_status}")
        else:
            print("❌ Master agent not found")
            return False
        
        # Test session creation
        session_id = await app.runtime.state_manager.create_session(language="zh")
        print(f"📝 Test session created: {session_id}")
        
        # Test message handling
        from fortune_teller.agents.base_agent import FortuneMessage
        
        test_message = FortuneMessage(
            type="user_interaction",
            sender="test_user",
            recipient="master_agent", 
            session_id=session_id,
            language="zh",
            payload={"content": "测试消息：我想了解塔罗牌"}
        )
        
        print("📤 Testing message handling...")
        response = await master_agent.handle_message(test_message)
        
        print(f"📥 Response received:")
        print(f"   Type: {response.type}")
        print(f"   Sender: {response.sender}")
        print(f"   Payload: {response.payload}")
        
        # Cleanup
        await app.shutdown()
        print("✅ Application shutdown completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 Starting Strands Application Test\n")
    
    success = await test_app_startup()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 Strands Application Test PASSED!")
        print("✅ The application is ready for user interaction")
    else:
        print("❌ Strands Application Test FAILED!")
        print("⚠️ Check the errors above for details")
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner crashed: {e}")
        sys.exit(1)