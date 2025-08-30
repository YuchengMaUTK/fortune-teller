"""
消息总线 - 智能体间消息传递
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
import time
import uuid

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """消息类型枚举"""
    USER_REQUEST = "user_request"
    FORTUNE_REQUEST = "fortune_request"
    CHAT_REQUEST = "chat_request"
    FORTUNE_RESPONSE = "fortune_response"
    CHAT_RESPONSE = "chat_response"
    ERROR_RESPONSE = "error_response"
    AGENT_COLLABORATION = "agent_collaboration"
    STATE_UPDATE = "state_update"
    ADMIN_COMMAND = "admin_command"
    STATUS_REPORT = "status_report"


@dataclass
class Message:
    """消息数据结构"""
    type: MessageType
    sender: str
    recipient: str
    session_id: str
    language: str = "zh"
    payload: Dict[str, Any] = None
    timestamp: Optional[str] = None
    correlation_id: Optional[str] = None
    message_id: Optional[str] = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = str(time.time())
        if self.payload is None:
            self.payload = {}


class MessageBus:
    """
    消息总线
    
    负责智能体间的消息传递、路由和管理。
    支持：
    - 点对点消息传递
    - 广播消息
    - 消息队列
    - 消息持久化
    - 错误处理和重试
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.message_history: List[Message] = []
        self.max_history_size = 10000
        self.running = False
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "active_queues": 0
        }
    
    async def initialize(self) -> None:
        """初始化消息总线"""
        logger.info("Initializing message bus")
        self.running = False
    
    async def start(self) -> None:
        """启动消息总线"""
        logger.info("Starting message bus")
        self.running = True
    
    async def stop(self) -> None:
        """停止消息总线"""
        logger.info("Stopping message bus")
        self.running = False
        
        # 清理消息队列
        for queue_name in list(self.message_queues.keys()):
            await self._cleanup_queue(queue_name)
    
    def subscribe(self, agent_name: str, message_handler: Callable) -> None:
        """
        订阅消息
        
        Args:
            agent_name: 智能体名称
            message_handler: 消息处理函数
        """
        self.subscribers[agent_name].append(message_handler)
        logger.debug(f"Agent {agent_name} subscribed to message bus")
    
    def unsubscribe(self, agent_name: str, message_handler: Callable) -> None:
        """
        取消订阅消息
        
        Args:
            agent_name: 智能体名称
            message_handler: 消息处理函数
        """
        if agent_name in self.subscribers:
            try:
                self.subscribers[agent_name].remove(message_handler)
                logger.debug(f"Agent {agent_name} unsubscribed from message bus")
            except ValueError:
                logger.warning(f"Handler not found for agent {agent_name}")
    
    async def send_message(self, message: Message) -> bool:
        """
        发送消息
        
        Args:
            message: 要发送的消息
            
        Returns:
            发送是否成功
        """
        if not self.running:
            logger.error("Message bus not running")
            return False
        
        try:
            # 记录消息历史
            self._add_to_history(message)
            
            # 更新统计
            self.stats["messages_sent"] += 1
            
            # 路由消息
            success = await self._route_message(message)
            
            if success:
                logger.debug(f"Message sent: {message.type} from {message.sender} to {message.recipient}")
            else:
                logger.error(f"Failed to route message: {message.message_id}")
                self.stats["errors"] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.stats["errors"] += 1
            return False
    
    async def broadcast_message(self, message: Message, exclude: Optional[List[str]] = None) -> int:
        """
        广播消息
        
        Args:
            message: 要广播的消息
            exclude: 排除的智能体列表
            
        Returns:
            成功接收消息的智能体数量
        """
        if not self.running:
            logger.error("Message bus not running")
            return 0
        
        exclude = exclude or []
        success_count = 0
        
        for agent_name in self.subscribers:
            if agent_name not in exclude:
                # 创建副本消息
                broadcast_message = Message(
                    type=message.type,
                    sender=message.sender,
                    recipient=agent_name,
                    session_id=message.session_id,
                    language=message.language,
                    payload=message.payload.copy(),
                    correlation_id=message.correlation_id
                )
                
                if await self.send_message(broadcast_message):
                    success_count += 1
        
        logger.debug(f"Broadcast message to {success_count} agents")
        return success_count
    
    async def _route_message(self, message: Message) -> bool:
        """
        路由消息到目标智能体
        
        Args:
            message: 要路由的消息
            
        Returns:
            路由是否成功
        """
        recipient = message.recipient
        
        # 检查是否有订阅者
        if recipient not in self.subscribers or not self.subscribers[recipient]:
            logger.warning(f"No subscribers for recipient: {recipient}")
            return False
        
        # 获取或创建消息队列
        if recipient not in self.message_queues:
            self.message_queues[recipient] = asyncio.Queue()
            self.stats["active_queues"] += 1
        
        # 将消息放入队列
        try:
            await self.message_queues[recipient].put(message)
            
            # 通知订阅者
            for handler in self.subscribers[recipient]:
                try:
                    # 异步调用处理函数
                    asyncio.create_task(handler(message))
                except Exception as e:
                    logger.error(f"Error calling message handler for {recipient}: {e}")
            
            self.stats["messages_received"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error routing message to {recipient}: {e}")
            return False
    
    async def get_message(self, agent_name: str, timeout: Optional[float] = None) -> Optional[Message]:
        """
        获取消息（从队列中）
        
        Args:
            agent_name: 智能体名称
            timeout: 超时时间（秒）
            
        Returns:
            消息，如果超时或队列为空则返回 None
        """
        if agent_name not in self.message_queues:
            return None
        
        try:
            if timeout:
                message = await asyncio.wait_for(
                    self.message_queues[agent_name].get(),
                    timeout=timeout
                )
            else:
                message = await self.message_queues[agent_name].get()
            
            return message
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Error getting message for {agent_name}: {e}")
            return None
    
    def _add_to_history(self, message: Message) -> None:
        """
        添加消息到历史记录
        
        Args:
            message: 要添加的消息
        """
        self.message_history.append(message)
        
        # 限制历史记录大小
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size//2:]
    
    async def _cleanup_queue(self, agent_name: str) -> None:
        """
        清理消息队列
        
        Args:
            agent_name: 智能体名称
        """
        if agent_name in self.message_queues:
            queue = self.message_queues[agent_name]
            
            # 清空队列
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            del self.message_queues[agent_name]
            self.stats["active_queues"] -= 1
            logger.debug(f"Cleaned up message queue for {agent_name}")
    
    def get_message_history(self, 
                          session_id: Optional[str] = None,
                          agent_name: Optional[str] = None,
                          limit: int = 100) -> List[Message]:
        """
        获取消息历史
        
        Args:
            session_id: 会话ID过滤
            agent_name: 智能体名称过滤
            limit: 返回数量限制
            
        Returns:
            消息历史列表
        """
        filtered_messages = self.message_history
        
        if session_id:
            filtered_messages = [msg for msg in filtered_messages if msg.session_id == session_id]
        
        if agent_name:
            filtered_messages = [msg for msg in filtered_messages 
                               if msg.sender == agent_name or msg.recipient == agent_name]
        
        return filtered_messages[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取消息总线状态
        
        Returns:
            状态信息
        """
        return {
            "running": self.running,
            "subscribers": {name: len(handlers) for name, handlers in self.subscribers.items()},
            "active_queues": len(self.message_queues),
            "message_history_size": len(self.message_history),
            "stats": self.stats.copy()
        }