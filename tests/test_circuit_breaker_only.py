#!/usr/bin/env python3
"""
Test just the circuit breaker functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fortune_teller.agents.base_agent import BaseFortuneAgent, AgentState


class TestAgent(BaseFortuneAgent):
    """Test implementation of BaseFortuneAgent"""
    
    def __init__(self):
        super().__init__("test_agent")
    
    async def validate_input(self, message):
        return {"content": "test"}
    
    async def process_data(self, validated_input):
        return {"processed": "test"}
    
    async def generate_reading(self, processed_data, language="zh"):
        return {"result": "test"}


async def main():
    agent = TestAgent()
    agent.circuit_breaker_threshold = 2
    
    await agent.initialize()
    
    print(f"Initial state: failures={agent.circuit_breaker_failures}, threshold={agent.circuit_breaker_threshold}")
    print(f"Circuit breaker open: {agent._is_circuit_breaker_open()}")
    
    # Record failures
    agent._record_failure()
    print(f"After 1 failure: failures={agent.circuit_breaker_failures}")
    print(f"Circuit breaker open: {agent._is_circuit_breaker_open()}")
    
    agent._record_failure()
    print(f"After 2 failures: failures={agent.circuit_breaker_failures}")
    print(f"Circuit breaker open: {agent._is_circuit_breaker_open()}")
    
    # Reset
    agent._record_success()
    print(f"After success: failures={agent.circuit_breaker_failures}")
    print(f"Circuit breaker open: {agent._is_circuit_breaker_open()}")
    
    await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())