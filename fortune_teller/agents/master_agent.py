"""
主控制智能体 - 负责请求路由和会话管理
"""

from typing import Dict, Any, Optional
import logging
from .base_agent import BaseFortuneAgent, FortuneMessage

logger = logging.getLogger(__name__)


class MasterAgent(BaseFortuneAgent):
    """
    主控制智能体
    
    负责：
    - 用户请求路由到相应的专业智能体
    - 会话状态管理
    - 智能体协调
    - 用户界面交互
    """
    
    def __init__(self, agent_name: str = "master_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_name, config)
        self.system_name = "master"
        self.display_name = "霄占主控制器"
        self.version = "2.0.0"
        self.available_agents = {}
        self.routing_rules = {}
        
        # 会话状态管理
        self.session_states = {}  # {session_id: {"system": "bazi", "step": "collecting_input", "data": {}}}
        
        # 注册专用消息处理器
        self.register_message_handler("user_interaction", self._handle_user_interaction)
        self.register_message_handler("fortune_request", self._handle_fortune_request)
        self.register_message_handler("agent_registration", self._handle_agent_registration)
    
    async def _setup_tools(self) -> None:
        """设置主控制智能体的工具"""
        await super()._setup_tools()
        # 主控制智能体可能需要的特定工具
        # 例如：路由规则管理、会话管理等
    
    async def _setup_message_handlers(self) -> None:
        """设置消息处理器"""
        await super()._setup_message_handlers()
        # 已在 __init__ 中注册了专用处理器
    
    async def _on_start(self) -> None:
        """启动后钩子"""
        await super()._on_start()
        await self._discover_agents()
        await self._load_routing_rules()
    
    async def validate_input(self, message: FortuneMessage) -> Dict[str, Any]:
        """验证用户输入"""
        payload = message.payload or {}
        
        if message.type == "user_interaction":
            content = payload.get("content", "").strip()
            if not content:
                raise ValueError("用户输入不能为空")
            
            return {
                "content": content,
                "session_id": message.session_id,
                "language": message.language
            }
        elif message.type == "fortune_request":
            system_type = payload.get("system_type")
            if not system_type:
                raise ValueError("Missing system_type in fortune request")
            
            if system_type not in self.available_agents:
                raise ValueError(f"Unknown fortune system: {system_type}")
            
            return payload
        else:
            # 对于其他消息类型，返回原始 payload
            return payload
    
    async def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求数据"""
        # 主控制智能体主要负责路由，不直接处理占卜数据
        # 可以在这里添加请求预处理逻辑
        return validated_input
    
    async def generate_reading(self, processed_data: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
        """生成响应（主要是路由信息）"""
        return {
            "routing_info": processed_data,
            "timestamp": self._get_timestamp(),
            "language": language,
            "agent": self.agent_name
        }
    
    # ==================== 专用消息处理器 ====================
    
    async def _handle_user_interaction(self, message: FortuneMessage) -> FortuneMessage:
        """处理用户交互消息 - 支持状态管理"""
        try:
            session_id = message.session_id
            content = message.payload.get("content", "").strip()
            
            # 获取或创建会话状态
            if session_id not in self.session_states:
                self.session_states[session_id] = {"system": None, "step": "menu", "data": {}}
            
            session_state = self.session_states[session_id]
            
            # 根据当前状态处理输入
            if session_state["step"] == "menu":
                return await self._handle_menu_selection(message, session_state)
            elif session_state["step"] == "collecting_input":
                return await self._handle_input_collection(message, session_state)
            else:
                # 重置到菜单状态
                session_state["step"] = "menu"
                return await self._handle_menu_selection(message, session_state)
                
        except Exception as e:
            logger.error(f"Error handling user interaction: {e}")
            return await self._handle_error(e, message)
    
    async def _handle_menu_selection(self, message: FortuneMessage, session_state: Dict) -> FortuneMessage:
        """处理菜单选择"""
        content = message.payload.get("content", "").strip()
        
        # 检查是否是数字选择
        if content in ["1", "2", "3"]:
            system_map = {"1": "bazi", "2": "tarot", "3": "zodiac"}
            selected_system = system_map[content]
            
            # 更新会话状态
            session_state["system"] = selected_system
            session_state["step"] = "collecting_input"
            session_state["data"] = {}
            
            # 获取I18n智能体
            i18n_agent = await self._get_agent_from_runtime("i18n_agent")
            language = message.language or "zh"
            
            # 对于八字，立即开始收集输入
            if selected_system == "bazi":
                if i18n_agent:
                    prompt_text = i18n_agent.get_text("bazi_selected", language) + "\n\n" + i18n_agent.get_text("bazi_birth_date_prompt", language)
                else:
                    prompt_text = "🀄 已选择八字命理系统\n\n请输入您的出生日期 (格式: YYYY-MM-DD，如 1990-01-15):"
                
                return FortuneMessage(
                    type="input_prompt",
                    sender=self.agent_name,
                    recipient=message.sender,
                    session_id=message.session_id,
                    language=language,
                    payload={
                        "message": prompt_text,
                        "next_field": "birth_date"
                    },
                    correlation_id=message.correlation_id
                )
            elif selected_system == "tarot":
                if i18n_agent:
                    prompt_text = i18n_agent.get_text("tarot_selected", language) + "\n\n" + i18n_agent.get_text("tarot_question_prompt", language)
                else:
                    prompt_text = "🃏 已选择塔罗牌系统\n\n请输入您想要咨询的问题 (如：我的事业发展如何？):"
                
                return FortuneMessage(
                    type="input_prompt",
                    sender=self.agent_name,
                    recipient=message.sender,
                    session_id=message.session_id,
                    language=language,
                    payload={
                        "message": prompt_text,
                        "next_field": "question"
                    },
                    correlation_id=message.correlation_id
                )
            elif selected_system == "zodiac":
                if i18n_agent:
                    prompt_text = i18n_agent.get_text("zodiac_selected", language) + "\n\n" + i18n_agent.get_text("zodiac_birth_date_prompt", language)
                else:
                    prompt_text = "⭐ 已选择星座占星系统\n\n请输入您的出生日期 (格式: YYYY-MM-DD，如 1990-01-15):"
                
                return FortuneMessage(
                    type="input_prompt",
                    sender=self.agent_name,
                    recipient=message.sender,
                    session_id=message.session_id,
                    language=language,
                    payload={
                        "message": prompt_text,
                        "next_field": "birth_date"
                    },
                    correlation_id=message.correlation_id
                )
            else:
                # 其他系统暂时直接路由
                return await self._route_to_system(message, selected_system)
        
        # 检查关键词
        intent = await self._analyze_user_intent(content)
        if intent["requires_routing"]:
            system_type = intent["system_type"]
            session_state["system"] = system_type
            session_state["step"] = "collecting_input"
            session_state["data"] = {}
            
            if system_type == "bazi":
                return FortuneMessage(
                    type="input_prompt",
                    sender=self.agent_name,
                    recipient=message.sender,
                    session_id=message.session_id,
                    language=message.language,
                    payload={
                        "message": f"🀄 已选择八字命理系统\n\n请输入您的出生日期 (格式: YYYY-MM-DD，如 1990-01-15):",
                        "next_field": "birth_date"
                    },
                    correlation_id=message.correlation_id
                )
            elif system_type == "zodiac":
                return FortuneMessage(
                    type="input_prompt",
                    sender=self.agent_name,
                    recipient=message.sender,
                    session_id=message.session_id,
                    language=message.language,
                    payload={
                        "message": f"⭐ 已选择星座占星系统\n\n请输入您的出生日期 (格式: YYYY-MM-DD，如 1990-01-15):",
                        "next_field": "birth_date"
                    },
                    correlation_id=message.correlation_id
                )
            else:
                return await self._route_to_system(message, system_type)
        
        # 显示菜单
        return await self._generate_direct_response(message, {"show_menu": True})
    
    async def _handle_input_collection(self, message: FortuneMessage, session_state: Dict) -> FortuneMessage:
        """处理输入收集阶段"""
        content = message.payload.get("content", "").strip()
        system_type = session_state["system"]
        
        # 尝试解析用户输入作为数据
        if system_type == "bazi":
            return await self._handle_bazi_input_collection(message, session_state, content)
        elif system_type == "tarot":
            return await self._handle_tarot_input_collection(message, session_state, content)
        elif system_type == "zodiac":
            return await self._handle_zodiac_input_collection(message, session_state, content)
        
        # 默认重置到菜单
        session_state["step"] = "menu"
        return await self._generate_direct_response(message, {"show_menu": True})
    
    async def _handle_bazi_input_collection(self, message: FortuneMessage, session_state: Dict, content: str) -> FortuneMessage:
        """处理八字输入收集"""
        data = session_state["data"]
        
        # 尝试解析日期格式 YYYY-MM-DD
        if not data.get("birth_date") and self._is_date_format(content):
            data["birth_date"] = content
            return FortuneMessage(
                type="input_prompt",
                sender=self.agent_name,
                recipient=message.sender,
                session_id=message.session_id,
                language=message.language,
                payload={
                    "message": f"✅ 出生日期: {content}\n\n请输入您的出生时间 (格式: HH:MM，如 14:30):",
                    "next_field": "birth_time"
                },
                correlation_id=message.correlation_id
            )
        
        # 尝试解析时间格式 HH:MM
        elif not data.get("birth_time") and self._is_time_format(content):
            data["birth_time"] = content
            return FortuneMessage(
                type="input_prompt",
                sender=self.agent_name,
                recipient=message.sender,
                session_id=message.session_id,
                language=message.language,
                payload={
                    "message": f"✅ 出生时间: {content}\n\n请输入您的性别 (男/女):",
                    "next_field": "gender"
                },
                correlation_id=message.correlation_id
            )
        
        # 性别输入
        elif not data.get("gender") and content.lower() in ["男", "女", "male", "female", "m", "f"]:
            data["gender"] = "男" if content.lower() in ["男", "male", "m"] else "女"
            
            # 收集完毕，进行八字计算
            session_state["step"] = "menu"  # 重置状态
            
            # 创建完整的消息发送给八字智能体
            fortune_message = FortuneMessage(
                type="fortune_request",
                sender=self.agent_name,
                recipient="bazi_agent",
                session_id=message.session_id,
                language=message.language,
                payload={
                    "birth_date": data["birth_date"],
                    "birth_time": data["birth_time"],
                    "gender": data["gender"],
                    "location": "中国"
                },
                correlation_id=message.correlation_id
            )
            
            return await self._route_to_system(fortune_message, "bazi")
        
        # 无法识别的输入，给出提示
        missing_fields = []
        if not data.get("birth_date"):
            missing_fields.append("出生日期 (格式: YYYY-MM-DD，如 1990-01-15)")
        elif not data.get("birth_time"):
            missing_fields.append("出生时间 (格式: HH:MM，如 14:30)")
        elif not data.get("gender"):
            missing_fields.append("性别 (男/女)")
        
        return FortuneMessage(
            type="input_prompt",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload={
                "message": f"❌ 输入格式不正确。\n\n还需要: {missing_fields[0] if missing_fields else '未知'}",
                "error": True
            },
            correlation_id=message.correlation_id
        )
    
    def _is_date_format(self, text: str) -> bool:
        """检查是否是日期格式"""
        import re
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', text))
    
    def _is_time_format(self, text: str) -> bool:
        """检查是否是时间格式"""
        import re
        return bool(re.match(r'^\d{1,2}:\d{2}$', text))
    
    async def _handle_tarot_input_collection(self, message: FortuneMessage, session_state: Dict, content: str) -> FortuneMessage:
        """处理塔罗输入收集"""
        data = session_state["data"]
        
        # 第一步：收集问题
        if not data.get("question") and content.strip():
            data["question"] = content.strip()
            
            # 显示牌阵选择
            spread_menu = """请选择塔罗牌阵：

1. 🃏 单牌阅读 - 抽取一张牌进行简单的阅读
2. 🔮 三牌阵 - 过去、现在、未来的经典三牌阵  
3. ✨ 凯尔特十字 - 详细分析当前情况和潜在结果的经典阵列
4. 💕 关系阵 - 分析两个人之间关系的牌阵

请选择 (1-4):"""
            
            return FortuneMessage(
                type="input_prompt",
                sender=self.agent_name,
                recipient=message.sender,
                session_id=message.session_id,
                language=message.language,
                payload={
                    "message": spread_menu,
                    "next_field": "spread"
                },
                correlation_id=message.correlation_id
            )
        
        # 第二步：收集牌阵选择
        elif data.get("question") and not data.get("spread") and content.strip() in ["1", "2", "3", "4"]:
            spread_map = {
                "1": "single",
                "2": "three_card", 
                "3": "celtic_cross",
                "4": "relationship"
            }
            data["spread"] = spread_map[content.strip()]
            
            # 收集完毕，进行塔罗占卜
            session_state["step"] = "menu"  # 重置状态
            
            # 创建完整的消息发送给塔罗智能体
            fortune_message = FortuneMessage(
                type="fortune_request",
                sender=self.agent_name,
                recipient="tarot_agent",
                session_id=message.session_id,
                language=message.language,
                payload={
                    "question": data["question"],
                    "spread_type": data["spread"],
                    "name": "缘主",
                    "focus_area": "综合运势"
                },
                correlation_id=message.correlation_id
            )
            
            return await self._route_to_system(fortune_message, "tarot")
        
        # 错误处理
        if not data.get("question"):
            return FortuneMessage(
                type="input_prompt",
                sender=self.agent_name,
                recipient=message.sender,
                session_id=message.session_id,
                language=message.language,
                payload={
                    "message": "❌ 请输入您的问题\n\n例如：我的事业发展如何？我的感情运势怎样？",
                    "error": True
                },
                correlation_id=message.correlation_id
            )
        else:
            return FortuneMessage(
                type="input_prompt",
                sender=self.agent_name,
                recipient=message.sender,
                session_id=message.session_id,
                language=message.language,
                payload={
                    "message": "❌ 请选择有效的牌阵 (1-4)",
                    "error": True
                },
                correlation_id=message.correlation_id
            )
    
    async def _handle_zodiac_input_collection(self, message: FortuneMessage, session_state: Dict, content: str) -> FortuneMessage:
        """处理星座输入收集"""
        data = session_state["data"]
        
        # 星座只需要出生日期
        if not data.get("birth_date") and self._is_date_format(content):
            data["birth_date"] = content
            
            # 收集完毕，进行星座分析
            session_state["step"] = "menu"  # 重置状态
            
            # 创建完整的消息发送给星座智能体
            fortune_message = FortuneMessage(
                type="fortune_request",
                sender=self.agent_name,
                recipient="zodiac_agent",
                session_id=message.session_id,
                language=message.language,
                payload={
                    "birth_date": data["birth_date"],
                    "name": "缘主"
                },
                correlation_id=message.correlation_id
            )
            
            return await self._route_to_system(fortune_message, "zodiac")
        
        # 如果格式不正确，提示输入
        return FortuneMessage(
            type="input_prompt",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload={
                "message": "❌ 日期格式不正确\n\n请输入出生日期 (格式: YYYY-MM-DD，如 1990-01-15):",
                "error": True
            },
            correlation_id=message.correlation_id
        )
    
    async def _handle_fortune_request(self, message: FortuneMessage) -> FortuneMessage:
        """处理占卜请求消息"""
        try:
            system_type = message.payload.get("system_type")
            return await self._route_to_system(message, system_type)
        except Exception as e:
            logger.error(f"Error handling fortune request: {e}")
            return await self._handle_error(e, message)
    
    async def _handle_agent_registration(self, message: FortuneMessage) -> FortuneMessage:
        """处理智能体注册消息"""
        try:
            agent_info = message.payload
            agent_name = agent_info.get("agent_name")
            agent_type = agent_info.get("agent_type")
            
            if agent_name and agent_type:
                self.available_agents[agent_type] = agent_name
                logger.info(f"Registered agent: {agent_name} for type: {agent_type}")
                
                return FortuneMessage(
                    type="registration_success",
                    sender=self.agent_name,
                    recipient=message.sender,
                    session_id=message.session_id,
                    language=message.language,
                    payload={"status": "registered", "agent_type": agent_type},
                    correlation_id=message.correlation_id
                )
            else:
                raise ValueError("Invalid agent registration data")
                
        except Exception as e:
            logger.error(f"Error handling agent registration: {e}")
            return await self._handle_error(e, message)
    
    # ==================== 路由和意图分析 ====================
    
    async def _analyze_user_intent(self, content: str, language: str = "zh") -> Dict[str, Any]:
        """分析用户意图"""
        content_lower = content.lower().strip()
        
        intent = {
            "requires_routing": False,
            "system_type": None,
            "confidence": 0.0,
            "keywords": [],
            "show_menu": False
        }
        
        # 检查是否是数字选择
        if content_lower in ["1", "2", "3"]:
            system_map = {"1": "bazi", "2": "tarot", "3": "zodiac"}
            intent["requires_routing"] = True
            intent["system_type"] = system_map[content_lower]
            intent["confidence"] = 1.0
            return intent
        
        # 检查是否需要显示菜单
        if content_lower in ["", "help", "帮助", "菜单", "选择", "系统", "list", "开始"]:
            intent["show_menu"] = True
            return intent
        
        # 检查占卜系统关键词
        system_keywords = {
            "bazi": ["八字", "命理", "生辰", "四柱", "五行"],
            "tarot": ["塔罗", "塔罗牌", "抽牌", "占卜"],
            "zodiac": ["星座", "占星", "星盘", "十二星座", "星象"]
        }
        
        for system_type, keywords in system_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    intent["requires_routing"] = True
                    intent["system_type"] = system_type
                    intent["confidence"] = 0.8
                    intent["keywords"].append(keyword)
                    break
            
            if intent["requires_routing"]:
                break
        
        # 如果没有明确的系统类型，显示菜单
        if not intent["requires_routing"]:
            intent["show_menu"] = True
        
        return intent
    
    async def _route_to_specialist(self, message: FortuneMessage, intent: Dict[str, Any]) -> FortuneMessage:
        """路由到专业智能体"""
        system_type = intent.get("system_type")
        
        if system_type == "general":
            # 需要进一步询问用户选择具体系统
            return FortuneMessage(
                type="system_selection_request",
                sender=self.agent_name,
                recipient=message.sender,
                session_id=message.session_id,
                language=message.language,
                payload={
                    "message": "我可以为您提供多种占卜服务，请选择您感兴趣的类型：",
                    "options": [
                        {"type": "bazi", "name": "八字命理", "description": "基于生辰八字的传统命理分析"},
                        {"type": "tarot", "name": "塔罗占卜", "description": "使用塔罗牌进行占卜解读"},
                        {"type": "zodiac", "name": "星座占星", "description": "基于星座和星盘的占星分析"}
                    ]
                },
                correlation_id=message.correlation_id
            )
        
        elif system_type in self.available_agents:
            # 实际路由到专业智能体
            agent_name = f"{system_type}_agent"  # bazi -> bazi_agent
            target_agent = await self._get_agent_from_runtime(agent_name)
            
            if target_agent:
                # 创建专业智能体消息
                fortune_message = FortuneMessage(
                    type="fortune_request",
                    sender=self.agent_name,
                    recipient=agent_name,
                    session_id=message.session_id,
                    language=message.language,
                    payload=message.payload,
                    correlation_id=message.correlation_id
                )
                
                # 处理占卜请求
                try:
                    # 验证输入
                    validated_input = await target_agent.validate_input(fortune_message)
                    
                    # 检查是否需要收集更多信息
                    if not validated_input.get("valid", False):
                        if validated_input.get("need_input", False):
                            return FortuneMessage(
                                type="input_request",
                                sender=self.agent_name,
                                recipient=message.sender,
                                session_id=message.session_id,
                                language=message.language,
                                payload={
                                    "system": system_type,
                                    "missing_fields": validated_input.get("missing_fields", {}),
                                    "current_data": validated_input.get("current_data", {}),
                                    "error": validated_input.get("error")
                                },
                                correlation_id=message.correlation_id
                            )
                        else:
                            return FortuneMessage(
                                type="error_response",
                                sender=self.agent_name,
                                recipient=message.sender,
                                session_id=message.session_id,
                                language=message.language,
                                payload={
                                    "error": "输入验证失败",
                                    "details": validated_input.get("error", "未知错误"),
                                    "system": system_type
                                },
                                correlation_id=message.correlation_id
                            )
                    
                    # 处理数据
                    processed_data = await target_agent.process_data(validated_input)
                    
                    # 生成解读
                    reading_result = await target_agent.generate_reading(processed_data, message.language)
                    
                    return FortuneMessage(
                        type="fortune_response",
                        sender=self.agent_name,
                        recipient=message.sender,
                        session_id=message.session_id,
                        language=message.language,
                        payload={
                            "system": system_type,
                            "result": reading_result,
                            "success": True
                        },
                        correlation_id=message.correlation_id
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing {system_type} request: {e}")
                    return FortuneMessage(
                        type="error_response",
                        sender=self.agent_name,
                        recipient=message.sender,
                        session_id=message.session_id,
                        language=message.language,
                        payload={
                            "error": "处理请求时发生错误",
                            "details": str(e),
                            "system": system_type
                        },
                        correlation_id=message.correlation_id
                    )
            else:
                # 后备：返回路由信息
                return FortuneMessage(
                    type="routing_response",
                    sender=self.agent_name,
                    recipient=message.sender,
                    session_id=message.session_id,
                    language=message.language,
                    payload={
                        "routed_to": system_type,
                        "message": f"正在为您连接{self._get_system_display_name(system_type)}服务...",
                        "confidence": intent.get("confidence", 0.0)
                    },
                    correlation_id=message.correlation_id
                )
        else:
            raise ValueError(f"No agent available for system: {system_type}")
    
    async def _route_to_system(self, message: FortuneMessage, system_type: str) -> FortuneMessage:
        """路由到指定系统 - 实际调用专业智能体"""
        if system_type not in self.available_agents:
            raise ValueError(f"Unknown fortune system: {system_type}")
        
        # 实际路由到专业智能体
        agent_name = f"{system_type}_agent"  # bazi -> bazi_agent
        target_agent = await self._get_agent_from_runtime(agent_name)
        
        if target_agent:
            try:
                # 验证输入
                validated_input = await target_agent.validate_input(message)
                
                # 如果验证失败，返回错误
                if not validated_input.get("valid", False):
                    return FortuneMessage(
                        type="error_response",
                        sender=self.agent_name,
                        recipient=message.sender,
                        session_id=message.session_id,
                        language=message.language,
                        payload={
                            "error": "输入验证失败",
                            "details": validated_input.get("error", "数据不完整"),
                            "system": system_type
                        },
                        correlation_id=message.correlation_id
                    )
                
                # 处理数据
                processed_data = await target_agent.process_data(validated_input)
                
                # 生成解读
                reading_result = await target_agent.generate_reading(processed_data, message.language)
                
                return FortuneMessage(
                    type="fortune_response",
                    sender=self.agent_name,
                    recipient=message.sender,
                    session_id=message.session_id,
                    language=message.language,
                    payload={
                        "system": system_type,
                        "result": reading_result,
                        "success": True
                    },
                    correlation_id=message.correlation_id
                )
                
            except Exception as e:
                logger.error(f"Error processing {system_type} request: {e}")
                return FortuneMessage(
                    type="error_response",
                    sender=self.agent_name,
                    recipient=message.sender,
                    session_id=message.session_id,
                    language=message.language,
                    payload={
                        "error": "处理请求时发生错误",
                        "details": str(e),
                        "system": system_type
                    },
                    correlation_id=message.correlation_id
                )
        else:
            # 后备：返回路由信息
            return FortuneMessage(
                type="routing_response",
                sender=self.agent_name,
                recipient=message.sender,
                session_id=message.session_id,
                language=message.language,
                payload={
                    "routed_to": system_type,
                    "message": f"请求已路由到{self._get_system_display_name(system_type)}智能体"
                },
                correlation_id=message.correlation_id
            )
    
    async def _generate_direct_response(self, message: FortuneMessage, intent: Dict[str, Any]) -> FortuneMessage:
        """生成直接响应"""
        # 获取I18n智能体
        i18n_agent = await self._get_agent_from_runtime("i18n_agent")
        language = message.language or "zh"
        
        # 如果需要显示菜单
        if intent.get("show_menu", False):
            if i18n_agent:
                # 使用I18n生成多语言菜单
                menu_text = f"""{i18n_agent.get_text('available_systems', language)}
------------------------------------------------------------
1. 🀄 {i18n_agent.get_text('system_bazi', language)} (bazi)
   {i18n_agent.get_text('desc_bazi', language)}
----------------------------------------
2. 🃏 {i18n_agent.get_text('system_tarot', language)} (tarot)
   {i18n_agent.get_text('desc_tarot', language)}
----------------------------------------
3. ⭐ {i18n_agent.get_text('system_zodiac', language)} (zodiac)
   {i18n_agent.get_text('desc_zodiac', language)}
----------------------------------------

💡 {i18n_agent.get_text('menu_instruction', language)}"""
            else:
                # 后备中文菜单
                menu_text = """✨ 可用的占卜系统 ✨
------------------------------------------------------------
1. 🀄 八字命理 (bazi)
   描述: 传统中国八字命理，基于出生年、月、日、时分析命运
----------------------------------------
2. 🃏 塔罗牌 (tarot)
   描述: 基于传统塔罗牌解读的占卜系统  
----------------------------------------
3. ⭐ 星座占星 (zodiac)
   描述: 基于西方占星学和十二星座的命运分析
----------------------------------------

💡 请选择:
• 输入数字 (1/2/3) 选择占卜系统
• 或直接说 "八字命理"、"塔罗牌"、"星座占星"
• 输入 "quit" 退出系统"""

            return FortuneMessage(
                type="system_menu",
                sender=self.agent_name,
                recipient=message.sender,
                session_id=message.session_id,
                language=message.language,
                payload={
                    "menu": menu_text,
                    "available_systems": {
                        "1": {"name": "八字命理", "system": "bazi"},
                        "2": {"name": "塔罗牌", "system": "tarot"}, 
                        "3": {"name": "星座占星", "system": "zodiac"}
                    }
                },
                correlation_id=message.correlation_id
            )
        
        # 默认帮助响应
        content = message.payload.get("content", "")
        response_text = (
            "您好！欢迎使用霄占命理系统。\n\n"
            "我可以为您提供以下服务：\n"
            "• 八字命理 - 基于生辰八字的传统命理分析\n"
            "• 塔罗占卜 - 使用塔罗牌进行占卜解读\n"
            "• 星座占星 - 基于星座和星盘的占星分析\n\n"
            "请告诉我您想了解哪种占卜服务，或者直接说出您的问题。"
        )
        
        return FortuneMessage(
            type="direct_response",
            sender=self.agent_name,
            recipient=message.sender,
            session_id=message.session_id,
            language=message.language,
            payload={
                "message": response_text,
                "suggestions": [
                    "我想算八字",
                    "我想抽塔罗牌", 
                    "我想看星座运势"
                ]
            },
            correlation_id=message.correlation_id
        )
    
    # ==================== 辅助方法 ====================
    
    async def _discover_agents(self) -> None:
        """发现可用的智能体"""
        # TODO: 实现智能体发现机制
        # 从运行时环境或配置中获取可用智能体
        self.available_agents = {
            "bazi": "BaZiAgent",
            "tarot": "TarotAgent", 
            "zodiac": "ZodiacAgent",
            "chat": "ChatAgent"
        }
        logger.info(f"Discovered agents: {list(self.available_agents.keys())}")
    
    async def _get_agent_from_runtime(self, agent_name: str):
        """从运行时获取智能体实例"""
        try:
            if hasattr(self, 'runtime') and self.runtime:
                return self.runtime.agents.get(agent_name)
            return None
        except Exception as e:
            logger.error(f"Failed to get agent {agent_name}: {e}")
            return None
    
    async def set_runtime(self, runtime):
        """设置运行时引用"""
        self.runtime = runtime
    
    async def _load_routing_rules(self) -> None:
        """加载路由规则"""
        # TODO: 从配置文件加载路由规则
        self.routing_rules = {
            "default_confidence_threshold": 0.7,
            "fallback_system": "chat"
        }
        logger.info("Routing rules loaded")
        """加载路由规则"""
        # TODO: 从配置加载路由规则
        self.routing_rules = {
            "bazi": {
                "keywords": ["八字", "命理", "生辰", "四柱", "五行"],
                "priority": 1
            },
            "tarot": {
                "keywords": ["塔罗", "塔罗牌", "抽牌", "占卜"],
                "priority": 1
            },
            "zodiac": {
                "keywords": ["星座", "占星", "星盘", "十二星座"],
                "priority": 1
            }
        }
        logger.debug("Routing rules loaded")
    
    def _get_system_display_name(self, system_type: str) -> str:
        """获取系统显示名称"""
        display_names = {
            "bazi": "八字命理",
            "tarot": "塔罗占卜",
            "zodiac": "星座占星",
            "chat": "智能对话"
        }
        return display_names.get(system_type, system_type)
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()