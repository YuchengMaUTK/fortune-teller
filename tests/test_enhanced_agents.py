#!/usr/bin/env python3
"""
Test the enhanced BaseFortuneAgent and MasterAgent implementations
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fortune_teller.agents.base_agent import BaseFortuneAgent, FortuneMessage, AgentState, MessagePriority
from fortune_teller.agents.master_agent import MasterAgent
from fortune_teller.ui.colors import Colors


class TestAgent(BaseFortuneAgent):
    """Test implementation of BaseFortuneAgent"""
    
    def __init__(self):
        super().__init__("test_agent")
        self.system_name = "test"
        self.display_name = "测试智能体"
    
    async def validate_input(self, message):
        """Test validation"""
        payload = message.payload or {}
        content = payload.get("content", "")
        if not content:
            raise ValueError("Content is required")
        return {"content": content}
    
    async def process_data(self, validated_input):
        """Test processing"""
        return {"processed": validated_input["content"].upper()}
    
    async def generate_reading(self, processed_data, language="zh"):
        """Test reading generation"""
        return {
            "result": f"测试结果: {processed_data['processed']}",
            "language": language
        }


async def test_base_agent_lifecycle():
    """Test BaseFortuneAgent lifecycle management"""
    print(f"{Colors.YELLOW}🧪 测试基础智能体生命周期管理{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}")
    
    try:
        agent = TestAgent()
        
        # Test initial state
        assert agent.state == AgentState.INITIALIZING
        print("✅ 初始状态正确")
        
        # Test initialization
        await agent.initialize()
        assert agent.state == AgentState.IDLE
        print("✅ 初始化成功")
        
        # Test status
        status = agent.get_status()
        assert status["agent_name"] == "test_agent"
        assert status["state"] == "idle"
        print("✅ 状态查询正常")
        
        # Test health status
        health = await agent.get_health_status()
        assert health["healthy"] == True
        print("✅ 健康检查正常")
        
        # Test message handling
        test_message = FortuneMessage(
            type="test_message",
            sender="test_user",
            recipient="test_agent",
            session_id="test_session",
            payload={"content": "hello world"}
        )
        
        response = await agent.handle_message(test_message)
        assert response.type == "test_message_response"
        assert "HELLO WORLD" in response.payload["result"]
        print("✅ 消息处理正常")
        
        # Test error handling
        error_message = FortuneMessage(
            type="test_message",
            sender="test_user",
            recipient="test_agent",
            session_id="test_session",
            payload={}  # Missing content
        )
        
        error_response = await agent.handle_message(error_message)
        assert error_response.type == "validation_error_response"
        print("✅ 错误处理正常")
        
        # Test shutdown
        await agent.shutdown()
        assert agent.state == AgentState.SHUTDOWN
        print("✅ 关闭流程正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 基础智能体测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_master_agent_enhanced():
    """Test enhanced MasterAgent functionality"""
    print(f"\n{Colors.YELLOW}🧪 测试增强版主控制智能体{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}")
    
    try:
        master = MasterAgent()
        
        # Test initialization
        await master.initialize()
        await master.start()
        assert master.state == AgentState.IDLE
        print("✅ 主控制智能体初始化成功")
        
        # Test user interaction with greeting
        greeting_message = FortuneMessage(
            type="user_interaction",
            sender="test_user",
            recipient="master_agent",
            session_id="test_session",
            payload={"content": "你好"}
        )
        
        response = await master.handle_message(greeting_message)
        assert response.type == "direct_response"
        assert "欢迎" in response.payload["message"]
        print("✅ 问候消息处理正常")
        
        # Test intent analysis for tarot
        tarot_message = FortuneMessage(
            type="user_interaction",
            sender="test_user",
            recipient="master_agent",
            session_id="test_session",
            payload={"content": "我想抽塔罗牌"}
        )
        
        response = await master.handle_message(tarot_message)
        assert response.type == "routing_response"
        assert response.payload["routed_to"] == "tarot"
        print("✅ 塔罗意图识别和路由正常")
        
        # Test intent analysis for bazi
        bazi_message = FortuneMessage(
            type="user_interaction",
            sender="test_user",
            recipient="master_agent",
            session_id="test_session",
            payload={"content": "我想算八字命理"}
        )
        
        response = await master.handle_message(bazi_message)
        assert response.type == "routing_response"
        assert response.payload["routed_to"] == "bazi"
        print("✅ 八字意图识别和路由正常")
        
        # Test general fortune request
        general_message = FortuneMessage(
            type="user_interaction",
            sender="test_user",
            recipient="master_agent",
            session_id="test_session",
            payload={"content": "我想算命"}
        )
        
        response = await master.handle_message(general_message)
        assert response.type == "system_selection_request"
        assert len(response.payload["options"]) > 0
        print("✅ 通用占卜请求处理正常")
        
        # Test fortune request message
        fortune_request = FortuneMessage(
            type="fortune_request",
            sender="test_user",
            recipient="master_agent",
            session_id="test_session",
            payload={"system_type": "zodiac"}
        )
        
        response = await master.handle_message(fortune_request)
        assert response.type == "routing_response"
        assert response.payload["routed_to"] == "zodiac"
        print("✅ 占卜请求消息处理正常")
        
        # Test agent registration
        registration_message = FortuneMessage(
            type="agent_registration",
            sender="new_agent",
            recipient="master_agent",
            session_id="system_session",
            payload={
                "agent_name": "new_test_agent",
                "agent_type": "test_system"
            }
        )
        
        response = await master.handle_message(registration_message)
        assert response.type == "registration_success"
        assert "test_system" in master.available_agents
        print("✅ 智能体注册功能正常")
        
        # Test health and status
        health = await master.get_health_status()
        assert health["healthy"] == True
        print("✅ 健康状态正常")
        
        status = master.get_status()
        assert status["agent_name"] == "master_agent"
        print("✅ 状态信息正常")
        
        # Test shutdown
        await master.shutdown()
        assert master.state == AgentState.SHUTDOWN
        print("✅ 关闭流程正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 主控制智能体测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_message_priority_and_retry():
    """Test message priority and retry mechanisms"""
    print(f"\n{Colors.YELLOW}🧪 测试消息优先级和重试机制{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}")
    
    try:
        # Test message creation with different priorities
        high_priority_msg = FortuneMessage(
            type="urgent_request",
            sender="test_user",
            recipient="test_agent",
            session_id="test_session",
            priority=MessagePriority.HIGH,
            payload={"content": "urgent message"}
        )
        
        assert high_priority_msg.priority == MessagePriority.HIGH
        assert high_priority_msg.message_id is not None
        assert high_priority_msg.timestamp is not None
        print("✅ 高优先级消息创建正常")
        
        # Test retry mechanism
        retry_msg = FortuneMessage(
            type="retry_test",
            sender="test_user",
            recipient="test_agent",
            session_id="test_session",
            retry_count=2,
            max_retries=3
        )
        
        assert retry_msg.retry_count == 2
        assert retry_msg.max_retries == 3
        print("✅ 重试机制参数正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 消息机制测试失败: {e}")
        return False


async def test_circuit_breaker():
    """Test circuit breaker functionality"""
    print(f"\n{Colors.YELLOW}🧪 测试熔断器功能{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}")
    
    try:
        agent = TestAgent()
        agent.circuit_breaker_threshold = 2  # 设置低阈值便于测试
        
        await agent.initialize()
        
        # Test normal operation
        assert not agent._is_circuit_breaker_open()
        print("✅ 熔断器初始状态正常")
        
        # Simulate failures
        agent._record_failure()
        agent._record_failure()
        
        # Circuit breaker should be open now
        is_open = agent._is_circuit_breaker_open()
        print(f"   熔断器状态: 失败次数={agent.circuit_breaker_failures}, 阈值={agent.circuit_breaker_threshold}, 开启={is_open}")
        assert is_open, f"Expected circuit breaker to be open, but it's not. Failures: {agent.circuit_breaker_failures}"
        print("✅ 熔断器开启正常")
        
        # Test success reset
        agent._record_success()
        is_open_after_reset = agent._is_circuit_breaker_open()
        print(f"   重置后状态: 失败次数={agent.circuit_breaker_failures}, 开启={is_open_after_reset}")
        assert not is_open_after_reset, "Expected circuit breaker to be closed after success"
        print("✅ 熔断器重置正常")
        
        await agent.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ 熔断器测试失败: {e}")
        return False


async def run_all_tests():
    """Run all enhanced agent tests"""
    print(f"{Colors.BOLD}🚀 开始增强版智能体测试{Colors.ENDC}\n")
    
    tests = [
        ("基础智能体生命周期", test_base_agent_lifecycle),
        ("增强版主控制智能体", test_master_agent_enhanced),
        ("消息优先级和重试", test_message_priority_and_retry),
        ("熔断器功能", test_circuit_breaker),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 崩溃: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{Colors.BOLD}📊 测试结果汇总{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✅ 通过{Colors.ENDC}" if result else f"{Colors.RED}❌ 失败{Colors.ENDC}"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 所有增强版智能体测试通过！{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ 任务 2.1 实现完成并验证成功{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}⚠️ 部分测试失败，请检查上述错误信息{Colors.ENDC}")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被用户中断{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}测试运行器崩溃: {e}{Colors.ENDC}")
        sys.exit(1)