"""
基础智能体类 - 所有占卜智能体的基类

本模块实现了基于 Strands Agents 框架的基础智能体类，
提供完整的生命周期管理、消息处理和错误处理机制。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
import time
import uuid
from datetime import datetime

# Import from strands-agents
from strands import Agent as StrandsAgent

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """智能体状态枚举"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"


class MessagePriority(Enum):
    """消息优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class FortuneMessage:
    """占卜消息数据结构"""
    type: str
    sender: str
    recipient: str
    session_id: str
    language: str = "zh"
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None
    correlation_id: Optional[str] = None
    message_id: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    timeout: Optional[float] = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())


@dataclass
class AgentMetrics:
    """智能体性能指标"""
    messages_processed: int = 0
    messages_failed: int = 0
    average_response_time: float = 0.0
    last_activity: Optional[str] = None
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    
    def update_response_time(self, response_time: float):
        """更新平均响应时间"""
        total_time = self.average_response_time * self.messages_processed
        self.messages_processed += 1
        self.average_response_time = (total_time + response_time) / self.messages_processed
        self.last_activity = datetime.now().isoformat()


class BaseFortuneAgent(StrandsAgent):
    """
    基础占卜智能体类 - 继承自 Strands Agents 框架
    
    所有专业占卜智能体都应该继承此类并实现抽象方法。
    提供完整的生命周期管理、消息处理和错误处理机制。
    
    主要功能：
    - 智能体生命周期管理（初始化、启动、停止、关闭）
    - 异步消息处理和路由
    - 错误处理和恢复机制
    - 性能监控和指标收集
    - 工具管理和集成
    - 状态持久化和恢复
    """
    
    def get_current_time(self) -> str:
        """获取当前时间戳"""
        return datetime.now().isoformat()
    
    async def get_tool(self, tool_name: str):
        """获取工具实例"""
        if hasattr(self, 'runtime') and self.runtime:
            return self.runtime.tools.get(tool_name)
        return None
    
    async def set_runtime(self, runtime):
        """设置运行时引用"""
        self.runtime = runtime
        logger.debug(f"Runtime set for agent {self.agent_name}")
    
    def __init__(self, agent_name: str, config: Optional[Dict[str, Any]] = None):
        # Initialize StrandsAgent with basic configuration
        config = config or {}
        system_prompt = config.get('system_prompt', f"You are {agent_name}, a fortune telling agent.")
        
        super().__init__(
            name=agent_name,
            system_prompt=system_prompt,
            agent_id=agent_name
        )
        
        # 基础属性
        self.agent_name = agent_name
        self.system_name = ""
        self.display_name = ""
        self.version = "1.0.0"
        self.config = config
        
        # 状态管理
        self.state = AgentState.INITIALIZING
        self.start_time = time.time()
        self.last_heartbeat = time.time()
        
        # 消息处理
        self.message_queue = asyncio.Queue()
        self.message_handlers: Dict[str, Callable] = {}
        self.active_sessions: Set[str] = set()
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        
        # 工具和依赖
        self.tools: Dict[str, Any] = {}
        self.dependencies: List[str] = []
        self.subscribers: List[str] = []
        
        # 性能监控
        self.metrics = AgentMetrics()
        self.health_check_interval = 30.0
        self.health_check_task: Optional[asyncio.Task] = None
        
        # 错误处理
        self.error_handlers: Dict[type, Callable] = {}
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset_time = 60.0
        self.circuit_breaker_failures = 0
        self.circuit_breaker_last_failure = 0.0
        
        # 日志
        self.logger = logging.getLogger(f"agent.{agent_name}")
        
        # 注册默认消息处理器
        self._register_default_handlers()
        
        # 注册默认错误处理器
        self._register_default_error_handlers()
    
    async def initialize(self) -> None:
        """
        初始化智能体
        
        执行智能体的完整初始化流程：
        1. 加载配置
        2. 初始化工具
        3. 设置消息处理器
        4. 启动健康检查
        5. 恢复持久化状态
        """
        try:
            self.logger.info(f"Initializing agent: {self.agent_name}")
            self.state = AgentState.INITIALIZING
            
            # 加载配置
            await self._load_configuration()
            
            # 初始化工具
            await self._setup_tools()
            
            # 设置消息处理器
            await self._setup_message_handlers()
            
            # 恢复持久化状态
            await self._restore_state()
            
            # 启动健康检查
            await self._start_health_check()
            
            # 标记为空闲状态
            self.state = AgentState.IDLE
            self.logger.info(f"Agent {self.agent_name} initialized successfully")
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.logger.error(f"Failed to initialize agent {self.agent_name}: {e}")
            raise
    
    async def start(self) -> None:
        """
        启动智能体
        
        启动智能体的消息处理循环和相关服务
        """
        try:
            if self.state != AgentState.IDLE:
                raise RuntimeError(f"Cannot start agent in state: {self.state}")
            
            self.logger.info(f"Starting agent: {self.agent_name}")
            
            # 启动消息处理循环
            asyncio.create_task(self._message_processing_loop())
            
            # 执行启动后钩子
            await self._on_start()
            
            self.logger.info(f"Agent {self.agent_name} started successfully")
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.logger.error(f"Failed to start agent {self.agent_name}: {e}")
            raise
    
    async def stop(self) -> None:
        """
        停止智能体
        
        优雅地停止智能体，完成当前处理的消息
        """
        try:
            self.logger.info(f"Stopping agent: {self.agent_name}")
            self.state = AgentState.SHUTTING_DOWN
            
            # 等待当前处理的任务完成
            if self.processing_tasks:
                self.logger.info(f"Waiting for {len(self.processing_tasks)} tasks to complete")
                await asyncio.gather(*self.processing_tasks.values(), return_exceptions=True)
            
            # 执行停止前钩子
            await self._on_stop()
            
            self.logger.info(f"Agent {self.agent_name} stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping agent {self.agent_name}: {e}")
            raise
    
    async def shutdown(self) -> None:
        """
        关闭智能体
        
        完全关闭智能体，清理所有资源
        """
        try:
            self.logger.info(f"Shutting down agent: {self.agent_name}")
            
            # 先停止智能体
            if self.state not in [AgentState.SHUTTING_DOWN, AgentState.SHUTDOWN]:
                await self.stop()
            
            self.state = AgentState.SHUTDOWN
            
            # 停止健康检查
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            # 持久化状态
            await self._persist_state()
            
            # 清理工具
            await self._cleanup_tools()
            
            # 执行关闭钩子
            await self._on_shutdown()
            
            self.logger.info(f"Agent {self.agent_name} shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown of agent {self.agent_name}: {e}")
            raise
    
    async def handle_message(self, message: FortuneMessage) -> FortuneMessage:
        """
        处理接收到的消息
        
        Args:
            message: 接收到的消息
            
        Returns:
            响应消息
        """
        start_time = time.time()
        
        try:
            # 检查智能体状态
            if self.state not in [AgentState.IDLE, AgentState.BUSY]:
                raise RuntimeError(f"Agent {self.agent_name} is not available (state: {self.state})")
            
            # 检查熔断器
            if self._is_circuit_breaker_open():
                raise RuntimeError(f"Circuit breaker is open for agent {self.agent_name}")
            
            # 更新状态
            old_state = self.state
            self.state = AgentState.BUSY
            
            # 添加会话跟踪
            self.active_sessions.add(message.session_id)
            
            self.logger.debug(f"Processing message: {message.type} from {message.sender}")
            
            # 查找消息处理器
            handler = self.message_handlers.get(message.type)
            if handler:
                # 使用专用处理器
                response = await handler(message)
            else:
                # 使用默认处理流程
                response = await self._default_message_processing(message)
            
            # 更新性能指标
            response_time = time.time() - start_time
            self.metrics.update_response_time(response_time)
            
            # 恢复状态
            self.state = old_state if old_state == AgentState.IDLE else AgentState.IDLE
            
            return response
            
        except Exception as e:
            # 错误处理
            response_time = time.time() - start_time
            self.metrics.messages_failed += 1
            
            # 更新熔断器
            self._record_failure()
            
            # 恢复状态
            self.state = AgentState.ERROR if isinstance(e, RuntimeError) else AgentState.IDLE
            
            self.logger.error(f"Error processing message: {e}")
            
            # 调用错误处理器
            error_response = await self._handle_error(e, message)
            return error_response
        
        finally:
            # 清理会话跟踪
            self.active_sessions.discard(message.session_id)
    
    async def _default_message_processing(self, message: FortuneMessage) -> FortuneMessage:
        """
        默认消息处理流程
        
        Args:
            message: 输入消息
            
        Returns:
            响应消息
        """
        # 验证输入
        validated_input = await self.validate_input(message)
        
        # 处理数据
        processed_data = await self.process_data(validated_input)
        
        # 生成解读
        reading = await self.generate_reading(processed_data, message.language)
        
        # 构建响应消息
        response = FortuneMessage(
            type=f"{message.type}_response",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload=reading,
            correlation_id=message.correlation_id
        )
        
        return response
    
    async def send_message(self, message: FortuneMessage) -> bool:
        """
        发送消息到其他智能体
        
        Args:
            message: 要发送的消息
            
        Returns:
            发送是否成功
        """
        try:
            # TODO: 集成到消息总线
            # await self.message_bus.send_message(message)
            self.logger.debug(f"Sending message: {message.type} to {message.recipient}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """
        注册消息处理器
        
        Args:
            message_type: 消息类型
            handler: 处理器函数
        """
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for message type: {message_type}")
    
    def unregister_message_handler(self, message_type: str) -> None:
        """
        取消注册消息处理器
        
        Args:
            message_type: 消息类型
        """
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]
            self.logger.debug(f"Unregistered handler for message type: {message_type}")
    
    @abstractmethod
    async def validate_input(self, message: FortuneMessage) -> Dict[str, Any]:
        """
        验证用户输入
        
        Args:
            message: 输入消息
            
        Returns:
            验证后的输入数据
            
        Raises:
            ValueError: 输入验证失败
        """
        pass
    
    @abstractmethod
    async def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理占卜数据
        
        Args:
            validated_input: 验证后的输入数据
            
        Returns:
            处理后的数据
        """
        pass
    
    @abstractmethod
    async def generate_reading(self, processed_data: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
        """
        生成占卜解读
        
        Args:
            processed_data: 处理后的数据
            language: 目标语言
            
        Returns:
            占卜解读结果
        """
        pass
    
    async def handle_followup(self, topic: str, context: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
        """
        处理后续询问
        
        Args:
            topic: 询问主题
            context: 上下文信息
            language: 目标语言
            
        Returns:
            后续询问的回答
        """
        # 默认实现，子类可以重写
        return {
            "response": f"关于{topic}的问题，我需要更多信息才能给出准确的回答。",
            "suggestions": ["请提供更具体的问题", "可以描述您的具体情况"]
        }
    
    # ==================== 错误处理和恢复机制 ====================
    
    async def _handle_error(self, error: Exception, message: FortuneMessage) -> FortuneMessage:
        """
        处理错误并生成错误响应
        
        Args:
            error: 发生的错误
            message: 原始消息
            
        Returns:
            错误响应消息
        """
        error_type = type(error).__name__
        
        # 查找专用错误处理器
        handler = self.error_handlers.get(type(error))
        if handler:
            try:
                return await handler(error, message)
            except Exception as e:
                self.logger.error(f"Error handler failed: {e}")
        
        # 默认错误处理
        error_payload = {
            "error": str(error),
            "error_type": error_type,
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "recoverable": self._is_recoverable_error(error)
        }
        
        return FortuneMessage(
            type="error_response",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload=error_payload,
            correlation_id=message.correlation_id
        )
    
    def register_error_handler(self, error_type: type, handler: Callable) -> None:
        """
        注册错误处理器
        
        Args:
            error_type: 错误类型
            handler: 错误处理器函数
        """
        self.error_handlers[error_type] = handler
        self.logger.debug(f"Registered error handler for: {error_type.__name__}")
    
    def _is_recoverable_error(self, error: Exception) -> bool:
        """
        判断错误是否可恢复
        
        Args:
            error: 错误实例
            
        Returns:
            是否可恢复
        """
        # 网络错误、超时错误等通常是可恢复的
        recoverable_errors = (
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
        )
        
        return isinstance(error, recoverable_errors)
    
    def _is_circuit_breaker_open(self) -> bool:
        """
        检查熔断器是否开启
        
        Returns:
            熔断器是否开启
        """
        if self.circuit_breaker_failures < self.circuit_breaker_threshold:
            return False
        
        # 检查是否超过重置时间
        if time.time() - self.circuit_breaker_last_failure > self.circuit_breaker_reset_time:
            self.circuit_breaker_failures = 0
            return False
        
        return True
    
    def _record_failure(self) -> None:
        """记录失败，更新熔断器状态"""
        self.circuit_breaker_failures += 1
        self.circuit_breaker_last_failure = time.time()
        
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.logger.warning(f"Circuit breaker opened for agent {self.agent_name}")
    
    def _record_success(self) -> None:
        """记录成功，重置熔断器"""
        if self.circuit_breaker_failures > 0:
            self.circuit_breaker_failures = 0
            self.logger.info(f"Circuit breaker reset for agent {self.agent_name}")
    
    # ==================== 生命周期钩子方法 ====================
    
    async def _on_start(self) -> None:
        """启动后钩子方法，子类可以重写"""
        pass
    
    async def _on_stop(self) -> None:
        """停止前钩子方法，子类可以重写"""
        pass
    
    async def _on_shutdown(self) -> None:
        """关闭钩子方法，子类可以重写"""
        pass
    
    # ==================== 内部辅助方法 ====================
    
    def _register_default_handlers(self) -> None:
        """注册默认消息处理器"""
        self.register_message_handler("ping", self._handle_ping)
        self.register_message_handler("health_check", self._handle_health_check)
        self.register_message_handler("get_status", self._handle_get_status)
    
    def _register_default_error_handlers(self) -> None:
        """注册默认错误处理器"""
        self.register_error_handler(ValueError, self._handle_validation_error)
        self.register_error_handler(TimeoutError, self._handle_timeout_error)
        self.register_error_handler(ConnectionError, self._handle_connection_error)
    
    async def _handle_ping(self, message: FortuneMessage) -> FortuneMessage:
        """处理 ping 消息"""
        return FortuneMessage(
            type="pong",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload={"timestamp": datetime.now().isoformat()},
            correlation_id=message.correlation_id
        )
    
    async def _handle_health_check(self, message: FortuneMessage) -> FortuneMessage:
        """处理健康检查消息"""
        health_status = await self.get_health_status()
        return FortuneMessage(
            type="health_check_response",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload=health_status,
            correlation_id=message.correlation_id
        )
    
    async def _handle_get_status(self, message: FortuneMessage) -> FortuneMessage:
        """处理状态查询消息"""
        status = self.get_status()
        return FortuneMessage(
            type="status_response",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload=status,
            correlation_id=message.correlation_id
        )
    
    async def _handle_validation_error(self, error: ValueError, message: FortuneMessage) -> FortuneMessage:
        """处理验证错误"""
        return FortuneMessage(
            type="validation_error_response",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload={
                "error": "输入验证失败",
                "details": str(error),
                "suggestions": ["请检查输入格式", "确保所有必填字段都已填写"]
            },
            correlation_id=message.correlation_id
        )
    
    async def _handle_timeout_error(self, error: TimeoutError, message: FortuneMessage) -> FortuneMessage:
        """处理超时错误"""
        return FortuneMessage(
            type="timeout_error_response",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload={
                "error": "请求超时",
                "details": "处理时间过长，请稍后重试",
                "retry_suggested": True
            },
            correlation_id=message.correlation_id
        )
    
    async def _handle_connection_error(self, error: ConnectionError, message: FortuneMessage) -> FortuneMessage:
        """处理连接错误"""
        return FortuneMessage(
            type="connection_error_response",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload={
                "error": "连接失败",
                "details": "无法连接到外部服务，请稍后重试",
                "retry_suggested": True
            },
            correlation_id=message.correlation_id
        ) 
   # ==================== 配置和状态管理 ====================
    
    async def _load_configuration(self) -> None:
        """加载智能体配置"""
        try:
            # TODO: 从配置管理器加载配置
            # config = await self.config_manager.get_agent_config(self.agent_name)
            # self.config.update(config)
            
            # 应用配置
            self.health_check_interval = self.config.get("health_check_interval", 30.0)
            self.circuit_breaker_threshold = self.config.get("circuit_breaker_threshold", 5)
            self.circuit_breaker_reset_time = self.config.get("circuit_breaker_reset_time", 60.0)
            
            self.logger.debug(f"Configuration loaded for agent {self.agent_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            # 使用默认配置继续
    
    async def _setup_tools(self) -> None:
        """设置智能体所需的工具"""
        try:
            # 子类可以重写此方法来设置特定工具
            # 默认实现为空
            self.logger.debug(f"Tools setup completed for agent {self.agent_name}")
        except Exception as e:
            self.logger.error(f"Failed to setup tools: {e}")
            raise
    
    async def _setup_message_handlers(self) -> None:
        """设置消息处理器"""
        try:
            # 子类可以重写此方法来注册特定的消息处理器
            self.logger.debug(f"Message handlers setup completed for agent {self.agent_name}")
        except Exception as e:
            self.logger.error(f"Failed to setup message handlers: {e}")
            raise
    
    async def _cleanup_tools(self) -> None:
        """清理工具资源"""
        try:
            for tool_name, tool in self.tools.items():
                if hasattr(tool, 'cleanup'):
                    await tool.cleanup()
                self.logger.debug(f"Cleaned up tool: {tool_name}")
            
            self.tools.clear()
            
        except Exception as e:
            self.logger.error(f"Error cleaning up tools: {e}")
    
    async def _restore_state(self) -> None:
        """恢复持久化状态"""
        try:
            # TODO: 从状态管理器恢复状态
            # state = await self.state_manager.get_agent_state(self.agent_name)
            # if state:
            #     self.metrics = AgentMetrics(**state.get("metrics", {}))
            
            self.logger.debug(f"State restored for agent {self.agent_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to restore state: {e}")
            # 继续使用默认状态
    
    async def _persist_state(self) -> None:
        """持久化状态"""
        try:
            # TODO: 保存状态到状态管理器
            # state = {
            #     "metrics": self.metrics.__dict__,
            #     "active_sessions": list(self.active_sessions),
            #     "last_heartbeat": self.last_heartbeat
            # }
            # await self.state_manager.set_agent_state(self.agent_name, state)
            
            self.logger.debug(f"State persisted for agent {self.agent_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to persist state: {e}")
    
    # ==================== 健康检查和监控 ====================
    
    async def _start_health_check(self) -> None:
        """启动健康检查任务"""
        if self.health_check_task is None:
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            self.logger.debug(f"Health check started for agent {self.agent_name}")
    
    async def _health_check_loop(self) -> None:
        """健康检查循环"""
        while self.state != AgentState.SHUTDOWN:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                if self.state == AgentState.SHUTDOWN:
                    break
                
                # 更新心跳
                self.last_heartbeat = time.time()
                
                # 更新运行时间
                self.metrics.uptime_seconds = time.time() - self.start_time
                
                # 更新内存使用（简化实现）
                try:
                    import psutil
                    import os
                    process = psutil.Process(os.getpid())
                    self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                except ImportError:
                    # psutil 不可用时跳过内存监控
                    self.metrics.memory_usage_mb = 0.0
                
                # 执行健康检查
                await self._perform_health_check()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
    
    async def _perform_health_check(self) -> None:
        """执行健康检查"""
        try:
            # 检查工具状态
            for tool_name, tool in self.tools.items():
                if hasattr(tool, 'health_check'):
                    health = await tool.health_check()
                    if not health.get('healthy', True):
                        self.logger.warning(f"Tool {tool_name} is unhealthy: {health}")
            
            # 检查消息队列大小
            queue_size = self.message_queue.qsize()
            if queue_size > 100:  # 阈值可配置
                self.logger.warning(f"Message queue size is high: {queue_size}")
            
            # 检查活跃会话数量
            if len(self.active_sessions) > 50:  # 阈值可配置
                self.logger.warning(f"High number of active sessions: {len(self.active_sessions)}")
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        获取健康状态
        
        Returns:
            健康状态信息
        """
        return {
            "agent_name": self.agent_name,
            "state": self.state.value,
            "healthy": self.state in [AgentState.IDLE, AgentState.BUSY],
            "uptime_seconds": time.time() - self.start_time,
            "last_heartbeat": self.last_heartbeat,
            "active_sessions": len(self.active_sessions),
            "message_queue_size": self.message_queue.qsize(),
            "circuit_breaker_failures": self.circuit_breaker_failures,
            "circuit_breaker_open": self._is_circuit_breaker_open(),
            "metrics": {
                "messages_processed": self.metrics.messages_processed,
                "messages_failed": self.metrics.messages_failed,
                "average_response_time": self.metrics.average_response_time,
                "memory_usage_mb": self.metrics.memory_usage_mb
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取智能体状态
        
        Returns:
            状态信息
        """
        return {
            "agent_name": self.agent_name,
            "system_name": self.system_name,
            "display_name": self.display_name,
            "version": self.version,
            "state": self.state.value,
            "uptime_seconds": time.time() - self.start_time,
            "active_sessions": len(self.active_sessions),
            "tools_count": len(self.tools),
            "message_handlers_count": len(self.message_handlers),
            "metrics": {
                "messages_processed": self.metrics.messages_processed,
                "messages_failed": self.metrics.messages_failed,
                "average_response_time": self.metrics.average_response_time,
                "last_activity": self.metrics.last_activity
            }
        }
    
    # ==================== 消息处理循环 ====================
    
    async def _message_processing_loop(self) -> None:
        """消息处理循环"""
        self.logger.info(f"Message processing loop started for agent {self.agent_name}")
        
        while self.state != AgentState.SHUTDOWN:
            try:
                # 从队列获取消息
                try:
                    message = await asyncio.wait_for(
                        self.message_queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # 处理消息
                task_id = f"{message.message_id}_{time.time()}"
                task = asyncio.create_task(self.handle_message(message))
                self.processing_tasks[task_id] = task
                
                # 等待处理完成并清理
                try:
                    await task
                finally:
                    self.processing_tasks.pop(task_id, None)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
        
        self.logger.info(f"Message processing loop stopped for agent {self.agent_name}")
    
    # ==================== 抽象方法 ====================
    
    @abstractmethod
    async def validate_input(self, message: FortuneMessage) -> Dict[str, Any]:
        """
        验证用户输入
        
        Args:
            message: 输入消息
            
        Returns:
            验证后的输入数据
            
        Raises:
            ValueError: 输入验证失败
        """
        pass
    
    @abstractmethod
    async def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理占卜数据
        
        Args:
            validated_input: 验证后的输入数据
            
        Returns:
            处理后的数据
        """
        pass
    
    @abstractmethod
    async def generate_reading(self, processed_data: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
        """
        生成占卜解读
        
        Args:
            processed_data: 处理后的数据
            language: 目标语言
            
        Returns:
            占卜解读结果
        """
        pass