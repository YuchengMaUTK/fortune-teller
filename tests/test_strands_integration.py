#!/usr/bin/env python3
"""
Test script for Strands Agents integration
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fortune_teller.runtime import StrandsRuntime
from fortune_teller.agents.base_agent import FortuneMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_basic_initialization():
    """Test basic runtime initialization"""
    print("🧪 Testing Strands Runtime Initialization...")
    
    try:
        runtime = StrandsRuntime()
        await runtime.initialize()
        
        print("✅ Runtime initialized successfully")
        
        # Check if components are loaded
        agents = runtime.list_agents()
        tools = runtime.list_tools()
        
        print(f"📋 Loaded agents: {agents}")
        print(f"🔧 Loaded tools: {tools}")
        
        # Get status
        status = runtime.get_status()
        print(f"📊 Runtime status: {status['runtime']}")
        
        await runtime.stop()
        print("✅ Runtime stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Runtime initialization failed: {e}")
        logger.exception("Runtime initialization error")
        return False


async def test_master_agent():
    """Test master agent functionality"""
    print("\n🧪 Testing Master Agent...")
    
    try:
        runtime = StrandsRuntime()
        await runtime.initialize()
        await runtime.start()
        
        # Get master agent
        master_agent = runtime.get_agent("master_agent")
        if not master_agent:
            print("❌ Master agent not found")
            return False
        
        print("✅ Master agent found")
        
        # Test message handling
        test_message = FortuneMessage(
            type="user_interaction",
            sender="test_user",
            recipient="master_agent",
            session_id="test_session_123",
            language="zh",
            payload={"content": "你好，我想算命"}
        )
        
        print("📤 Sending test message to master agent...")
        response = await master_agent.handle_message(test_message)
        
        print(f"📥 Received response: {response.type}")
        print(f"📝 Response payload: {response.payload}")
        
        await runtime.stop()
        print("✅ Master agent test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Master agent test failed: {e}")
        logger.exception("Master agent test error")
        return False


async def test_tools():
    """Test tool functionality"""
    print("\n🧪 Testing Tools...")
    
    try:
        runtime = StrandsRuntime()
        await runtime.initialize()
        
        # Test LLM tool
        llm_tool = runtime.get_tool("llm_tool")
        if llm_tool:
            print("✅ LLM tool found")
            health = await llm_tool.health_check()
            print(f"🏥 LLM tool health: {health}")
        else:
            print("⚠️ LLM tool not found")
        
        # Test Date tool
        date_tool = runtime.get_tool("date_tool")
        if date_tool:
            print("✅ Date tool found")
            health = await date_tool.health_check()
            print(f"🏥 Date tool health: {health}")
        else:
            print("⚠️ Date tool not found")
        
        await runtime.stop()
        print("✅ Tools test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        logger.exception("Tools test error")
        return False


async def test_message_bus():
    """Test message bus functionality"""
    print("\n🧪 Testing Message Bus...")
    
    try:
        runtime = StrandsRuntime()
        await runtime.initialize()
        await runtime.start()
        
        message_bus = runtime.message_bus
        
        # Test message creation and sending
        test_message = FortuneMessage(
            type="user_interaction",
            sender="test_sender",
            recipient="test_recipient",
            session_id="test_session",
            payload={"test": "data"}
        )
        
        # Subscribe a test handler
        received_messages = []
        
        async def test_handler(message):
            received_messages.append(message)
        
        message_bus.subscribe("test_recipient", test_handler)
        
        # Send message
        success = await message_bus.send_message(test_message)
        print(f"📤 Message sent: {success}")
        
        # Wait a bit for async processing
        await asyncio.sleep(0.1)
        
        print(f"📥 Messages received: {len(received_messages)}")
        
        # Get message bus status
        status = message_bus.get_status()
        print(f"📊 Message bus status: {status}")
        
        await runtime.stop()
        print("✅ Message bus test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Message bus test failed: {e}")
        logger.exception("Message bus test error")
        return False


async def test_state_manager():
    """Test state manager functionality"""
    print("\n🧪 Testing State Manager...")
    
    try:
        runtime = StrandsRuntime()
        await runtime.initialize()
        await runtime.start()
        
        state_manager = runtime.state_manager
        
        # Create a test session
        session_id = await state_manager.create_session(user_id="test_user", language="zh")
        print(f"📝 Created session: {session_id}")
        
        # Get session
        session = await state_manager.get_session(session_id)
        if session:
            print(f"✅ Retrieved session: {session.session_id}")
            print(f"👤 User ID: {session.user_id}")
            print(f"🌐 Language: {session.language}")
        else:
            print("❌ Failed to retrieve session")
        
        # Update session
        success = await state_manager.update_session(session_id, {
            "current_system": "tarot",
            "preferences": {"theme": "dark"}
        })
        print(f"📝 Session updated: {success}")
        
        # Test cache
        await state_manager.set_cache("test_key", {"test": "value"}, ttl=60)
        cached_value = await state_manager.get_cache("test_key")
        print(f"💾 Cache test: {cached_value}")
        
        # Get status
        status = state_manager.get_status()
        print(f"📊 State manager status: {status}")
        
        await runtime.stop()
        print("✅ State manager test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ State manager test failed: {e}")
        logger.exception("State manager test error")
        return False


async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Strands Agents Integration Tests\n")
    
    tests = [
        ("Basic Initialization", test_basic_initialization),
        ("Master Agent", test_master_agent),
        ("Tools", test_tools),
        ("Message Bus", test_message_bus),
        ("State Manager", test_state_manager),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Strands integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner crashed: {e}")
        sys.exit(1)