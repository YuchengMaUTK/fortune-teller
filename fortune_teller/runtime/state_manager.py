"""
状态管理器 - 会话状态和数据持久化
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """会话状态数据结构"""
    session_id: str
    user_id: Optional[str] = None
    language: str = "zh"
    current_system: Optional[str] = None
    last_reading: Optional[Dict] = None
    chat_context: List[Dict] = None
    created_at: str = None
    updated_at: str = None
    fortune_history: List[Dict] = None
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        current_time = str(time.time())
        if self.created_at is None:
            self.created_at = current_time
        if self.updated_at is None:
            self.updated_at = current_time
        if self.chat_context is None:
            self.chat_context = []
        if self.fortune_history is None:
            self.fortune_history = []
        if self.preferences is None:
            self.preferences = {}


class StateManager:
    """
    状态管理器
    
    负责：
    - 会话状态管理
    - 数据持久化
    - 状态同步
    - 缓存管理
    - 状态清理
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("data/sessions")
        self.active_sessions: Dict[str, SessionState] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, float] = {}
        self.running = False
        self.cleanup_interval = 300  # 5分钟
        self.session_timeout = 3600  # 1小时
        self.cleanup_task = None
        
        # 统计信息
        self.stats = {
            "active_sessions": 0,
            "total_sessions_created": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "persistence_operations": 0
        }
    
    async def initialize(self) -> None:
        """初始化状态管理器"""
        logger.info("Initializing state manager")
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 加载持久化的会话
        await self._load_persisted_sessions()
        
        self.running = False
    
    async def start(self) -> None:
        """启动状态管理器"""
        logger.info("Starting state manager")
        self.running = True
        
        # 启动清理任务
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self) -> None:
        """停止状态管理器"""
        logger.info("Stopping state manager")
        self.running = False
        
        # 停止清理任务
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # 持久化所有活跃会话
        await self._persist_all_sessions()
    
    async def create_session(self, 
                           user_id: Optional[str] = None,
                           language: str = "zh") -> str:
        """
        创建新会话
        
        Args:
            user_id: 用户ID
            language: 语言设置
            
        Returns:
            会话ID
        """
        session_id = str(uuid.uuid4())
        
        session_state = SessionState(
            session_id=session_id,
            user_id=user_id,
            language=language
        )
        
        self.active_sessions[session_id] = session_state
        self.stats["active_sessions"] = len(self.active_sessions)
        self.stats["total_sessions_created"] += 1
        
        logger.debug(f"Created session: {session_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        获取会话状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话状态，如果不存在则返回 None
        """
        # 首先检查活跃会话
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.updated_at = str(time.time())
            return session
        
        # 尝试从持久化存储加载
        session = await self._load_session(session_id)
        if session:
            self.active_sessions[session_id] = session
            self.stats["active_sessions"] = len(self.active_sessions)
            session.updated_at = str(time.time())
        
        return session
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新会话状态
        
        Args:
            session_id: 会话ID
            updates: 更新数据
            
        Returns:
            更新是否成功
        """
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        # 更新字段
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.updated_at = str(time.time())
        
        # 异步持久化
        asyncio.create_task(self._persist_session(session))
        
        logger.debug(f"Updated session: {session_id}")
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            删除是否成功
        """
        # 从活跃会话中删除
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            self.stats["active_sessions"] = len(self.active_sessions)
        
        # 从持久化存储中删除
        session_file = self.storage_path / f"{session_id}.json"
        if session_file.exists():
            try:
                session_file.unlink()
                logger.debug(f"Deleted session file: {session_id}")
            except Exception as e:
                logger.error(f"Error deleting session file {session_id}: {e}")
                return False
        
        logger.debug(f"Deleted session: {session_id}")
        return True
    
    async def set_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
        """
        self.cache[key] = value
        
        if ttl:
            self.cache_ttl[key] = time.time() + ttl
        
        logger.debug(f"Set cache: {key}")
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或过期则返回 None
        """
        # 检查是否过期
        if key in self.cache_ttl:
            if time.time() > self.cache_ttl[key]:
                # 过期，删除缓存
                del self.cache[key]
                del self.cache_ttl[key]
                self.stats["cache_misses"] += 1
                return None
        
        if key in self.cache:
            self.stats["cache_hits"] += 1
            return self.cache[key]
        else:
            self.stats["cache_misses"] += 1
            return None
    
    async def delete_cache(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            删除是否成功
        """
        deleted = False
        
        if key in self.cache:
            del self.cache[key]
            deleted = True
        
        if key in self.cache_ttl:
            del self.cache_ttl[key]
        
        return deleted
    
    async def _load_persisted_sessions(self) -> None:
        """加载持久化的会话"""
        if not self.storage_path.exists():
            return
        
        session_files = list(self.storage_path.glob("*.json"))
        loaded_count = 0
        
        for session_file in session_files:
            try:
                session = await self._load_session_from_file(session_file)
                if session:
                    # 检查会话是否过期
                    if self._is_session_expired(session):
                        # 删除过期会话
                        session_file.unlink()
                        continue
                    
                    self.active_sessions[session.session_id] = session
                    loaded_count += 1
            except Exception as e:
                logger.error(f"Error loading session from {session_file}: {e}")
        
        self.stats["active_sessions"] = len(self.active_sessions)
        logger.info(f"Loaded {loaded_count} persisted sessions")
    
    async def _load_session(self, session_id: str) -> Optional[SessionState]:
        """从持久化存储加载会话"""
        session_file = self.storage_path / f"{session_id}.json"
        return await self._load_session_from_file(session_file)
    
    async def _load_session_from_file(self, session_file: Path) -> Optional[SessionState]:
        """从文件加载会话"""
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            session = SessionState(**session_data)
            return session
            
        except Exception as e:
            logger.error(f"Error loading session from {session_file}: {e}")
            return None
    
    async def _persist_session(self, session: SessionState) -> None:
        """持久化会话"""
        session_file = self.storage_path / f"{session.session_id}.json"
        
        try:
            session_data = asdict(session)
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            self.stats["persistence_operations"] += 1
            logger.debug(f"Persisted session: {session.session_id}")
            
        except Exception as e:
            logger.error(f"Error persisting session {session.session_id}: {e}")
    
    async def _persist_all_sessions(self) -> None:
        """持久化所有活跃会话"""
        for session in self.active_sessions.values():
            await self._persist_session(session)
        
        logger.info(f"Persisted {len(self.active_sessions)} active sessions")
    
    def _is_session_expired(self, session: SessionState) -> bool:
        """检查会话是否过期"""
        try:
            updated_time = float(session.updated_at)
            return time.time() - updated_time > self.session_timeout
        except (ValueError, TypeError):
            return True
    
    async def _cleanup_loop(self) -> None:
        """清理循环任务"""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_sessions()
                await self._cleanup_expired_cache()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_expired_sessions(self) -> None:
        """清理过期会话"""
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.delete_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    async def _cleanup_expired_cache(self) -> None:
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, expire_time in self.cache_ttl.items():
            if current_time > expire_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self.delete_cache(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取状态管理器状态
        
        Returns:
            状态信息
        """
        return {
            "running": self.running,
            "storage_path": str(self.storage_path),
            "active_sessions": len(self.active_sessions),
            "cache_entries": len(self.cache),
            "session_timeout": self.session_timeout,
            "cleanup_interval": self.cleanup_interval,
            "stats": self.stats.copy()
        }