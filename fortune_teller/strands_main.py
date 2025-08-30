"""
霄占 Strands Agents 主入口

基于 Strands Agents 框架的多智能体占卜系统主程序。
保持原有的终端交互体验，同时利用多智能体架构的优势。
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path
from typing import Optional

from .runtime import StrandsRuntime
from .ui.display import print_welcome_screen
from .ui.colors import Colors

def print_error(message: str):
    """Print error message with red color"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fortune_teller_strands.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class FortunetellerStrandsApp:
    """
    霄占 Strands Agents 应用程序
    
    整合 Strands Agents 运行时和传统终端界面，
    为用户提供无缝的占卜体验。
    """
    
    def __init__(self, config_root: Optional[str] = None):
        self.runtime = StrandsRuntime(config_root)
        self.running = False
        self.current_session_id = None
        self.current_prompt = "请选择占卜系统或输入问题 (输入 'quit' 退出): "  # 动态提示符
        self.chat_mode = False  # 聊天模式标志
        self.last_fortune_reading = None  # 最后的占卜结果
        self.current_language = "zh"  # 当前语言
        self.i18n_agent = None  # 国际化智能体
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def initialize(self) -> bool:
        """初始化应用程序"""
        try:
            logger.info("Initializing Fortune Teller Strands application")
            
            # 初始化 Strands 运行时
            await self.runtime.initialize()
            
            # 启动运行时
            await self.runtime.start()
            
            # 获取国际化智能体
            self.i18n_agent = self.runtime.get_agent("i18n_agent")
            
            # 显示欢迎信息和语言选择
            await self._show_welcome_and_language_selection()
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            print_error(f"初始化失败: {e}")
            return False
    
    async def _show_welcome_and_language_selection(self):
        """显示欢迎信息和语言选择"""
        from .ui.colors import Colors
        
        # 显示标题
        print(f"{Colors.CYAN}")
        print("""
    ██╗  ██╗██╗ █████╗  ██████╗      ███████╗██╗  ██╗ █████╗ ███╗   ██╗
    ╚██╗██╔╝██║██╔══██╗██╔═══██╗     ╚══███╔╝██║  ██║██╔══██╗████╗  ██║
     ╚███╔╝ ██║███████║██║   ██║       ███╔╝ ███████║███████║██╔██╗ ██║
     ██╔██╗ ██║██╔══██║██║   ██║      ███╔╝  ██╔══██║██╔══██║██║╚██╗██║
    ██╔╝ ██╗██║██║  ██║╚██████╔╝     ███████╗██║  ██║██║  ██║██║ ╚████║
    ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝      ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
        """)
        print(f"{Colors.ENDC}")
        
        # 语言选择
        print(f"{Colors.BOLD}{Colors.YELLOW}Welcome to Fortune Teller / 欢迎使用霄占{Colors.ENDC}")
        print(f"{Colors.CYAN}✨ Ancient Wisdom at Your Fingertips / 古今命理，尽在掌握 ✨{Colors.ENDC}")
        print()
        print("=" * 80)
        print()
        # 语言选择 - 使用键盘导航和i18n
        from .ui.keyboard_input import select_language
        from .i18n import t
        
        try:
            selected_language = select_language()
            if selected_language is None:
                print(f"\n{Colors.YELLOW}{t('status_cancelled', 'zh')}{Colors.ENDC}")
                return
            
            self.current_language = selected_language
            
            # 显示选择结果
            status_msg = f"{Colors.GREEN}✓ {t('language_english', 'en')} {t('status_selected', 'en')}{Colors.ENDC}"
            if self.current_language == "zh":
                status_msg = f"{Colors.GREEN}✓ {t('language_chinese', 'zh')} {t('status_selected', 'zh')}{Colors.ENDC}"
            
            print(f"\n{status_msg}")
            self.current_prompt = t('navigation_select', self.current_language)
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}{t('status_cancelled', self.current_language)}{Colors.ENDC}")
            return
        
        print("\n" + "=" * 80)
        print()
        
        # 生成会话ID
        import uuid
        self.current_session_id = str(uuid.uuid4())
        print(f"{Colors.CYAN}{self.i18n_agent.get_text('session_id', self.current_language)}: {Colors.YELLOW}{self.current_session_id}{Colors.ENDC}")
        print()
    
    async def run(self) -> None:
        """运行应用程序"""
        if not await self.initialize():
            return
        
        try:
            # 显示欢迎界面
            print_welcome_screen()
            
            # 获取主控制智能体
            master_agent = self.runtime.get_agent("master_agent")
            if not master_agent:
                print_error("主控制智能体未找到，请检查配置")
                return
            
            # 创建会话
            self.current_session_id = await self.runtime.state_manager.create_session()
            
            print(f"{Colors.CYAN}欢迎使用霄占命理系统 (Strands Agents 版本)!{Colors.ENDC}")
            print(f"{Colors.YELLOW}会话ID: {self.current_session_id}{Colors.ENDC}")
            print()
            
            self.running = True
            
            # 主交互循环
            await self._main_loop(master_agent)
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}用户中断，正在退出...{Colors.ENDC}")
        except Exception as e:
            logger.error(f"Application error: {e}")
            print_error(f"应用程序错误: {e}")
        finally:
            await self.shutdown()
    
    async def _main_loop(self, master_agent) -> None:
        """主交互循环"""
        
        # 显示启动菜单
        await self._show_startup_menu(master_agent)
        
        while self.running:
            try:
                # 获取用户输入
                user_input = await self._get_user_input()
                
                if not user_input or user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    break
                
                # 处理用户输入
                await self._process_user_input(master_agent, user_input)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                print_error(f"处理错误: {e}")
    
    async def _show_startup_menu(self, master_agent) -> None:
        """显示启动菜单"""
        from .agents.base_agent import FortuneMessage
        
        # 创建显示菜单的消息
        message = FortuneMessage(
            type="user_interaction",
            sender="user",
            recipient="master_agent",
            session_id=self.current_session_id,
            language=self.current_language,  # 使用选择的语言
            payload={"content": "help"}  # 触发菜单显示
        )
        
        # 获取菜单响应
        response = await master_agent.handle_message(message)
        
        # 显示菜单
        await self._display_response(response)
    
    async def _get_user_input(self) -> str:
        """获取用户输入"""
        print(f"{Colors.GREEN}{self.current_prompt}{Colors.ENDC}", end="")
        
        # 在异步环境中获取用户输入
        loop = asyncio.get_event_loop()
        user_input = await loop.run_in_executor(None, input)
        
        return user_input.strip()
    
    async def _process_user_input(self, master_agent, user_input: str) -> None:
        """处理用户输入"""
        try:
            # 检查是否在聊天模式
            if self.chat_mode and user_input.strip() and user_input.strip() not in ["1", "2", "3"]:
                # 发送到聊天智能体
                from .agents.base_agent import FortuneMessage
                
                chat_message = FortuneMessage(
                    type="chat_request",
                    sender="user",
                    recipient="chat_agent",
                    session_id=self.current_session_id,
                    language=self.current_language,  # 使用当前语言
                    payload={
                        "message": user_input,
                        "previous_reading": self.last_fortune_reading
                    }
                )
                
                # 获取聊天智能体
                chat_agent = self.runtime.get_agent("chat_agent")
                if chat_agent:
                    try:
                        # 验证输入
                        validated_input = await chat_agent.validate_input(chat_message)
                        
                        # 处理数据
                        processed_data = await chat_agent.process_data(validated_input)
                        
                        # 生成回复
                        chat_result = await chat_agent.generate_reading(processed_data, "zh")
                        
                        # 创建聊天响应
                        chat_response = FortuneMessage(
                            type="chat_response",
                            sender="chat_agent",
                            recipient="user",
                            session_id=self.current_session_id,
                            language="zh",
                            payload={
                                "response": chat_result.get("response", ""),
                                "success": True
                            }
                        )
                        
                        await self._display_response(chat_response)
                        return
                        
                    except Exception as e:
                        logger.error(f"Chat processing error: {e}")
                        print(f"{Colors.RED}❌ 聊天处理错误: {e}{Colors.ENDC}")
                        return
            
            # 检查是否要退出聊天模式
            if self.chat_mode and user_input.strip() in ["1", "2", "3"]:
                self.chat_mode = False
                # 根据语言设置提示符
                if self.current_language == "en":
                    self.current_prompt = "Please select (1/2/3): "
                else:
                    self.current_prompt = "请选择 (1/2/3): "
            
            # 构建消息
            from .agents.base_agent import FortuneMessage
            
            message = FortuneMessage(
                type="user_interaction",
                sender="user",
                recipient="master_agent",
                session_id=self.current_session_id,
                language=self.current_language,  # 使用当前语言
                payload={"content": user_input}
            )
            
            # 发送给主控制智能体处理
            response = await master_agent.handle_message(message)
            
            # 显示响应
            await self._display_response(response)
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            print_error(f"处理用户输入时出错: {e}")
    
    async def _display_response(self, response) -> None:
        """
        显示智能体响应
        
        Args:
            response: 智能体响应消息
        """
        try:
            if response.type == "error_response":
                error_info = response.payload.get("error", "未知错误")
                print_error(f"系统错误: {error_info}")
            elif response.type == "input_prompt":
                # 显示输入提示
                message = response.payload.get("message", "")
                is_error = response.payload.get("error", False)
                next_field = response.payload.get("next_field", "")
                
                if is_error:
                    print(f"{Colors.RED}{message}{Colors.ENDC}")
                    # 根据语言设置错误提示符
                    if self.current_language == "en":
                        self.current_prompt = "Please re-enter: "
                    else:
                        self.current_prompt = "请重新输入: "
                else:
                    print(f"{Colors.CYAN}{message}{Colors.ENDC}")
                    # 根据下一个字段设置提示符
                    if next_field == "birth_date":
                        if self.current_language == "en":
                            self.current_prompt = "Birth date: "
                        else:
                            self.current_prompt = "出生日期: "
                    elif next_field == "birth_time":
                        if self.current_language == "en":
                            self.current_prompt = "Birth time: "
                        else:
                            self.current_prompt = "出生时间: "
                    elif next_field == "gender":
                        if self.current_language == "en":
                            self.current_prompt = "Gender: "
                        else:
                            self.current_prompt = "性别: "
                    elif next_field == "question":
                        if self.current_language == "en":
                            self.current_prompt = "Your question: "
                        else:
                            self.current_prompt = "您的问题: "
                    elif next_field == "spread":
                        if self.current_language == "en":
                            self.current_prompt = "Select spread (1-4): "
                        else:
                            self.current_prompt = "选择牌阵 (1-4): "
                    else:
                        if self.current_language == "en":
                            self.current_prompt = "Please enter: "
                        else:
                            self.current_prompt = "请输入: "
                
            elif response.type == "system_menu":
                # 显示系统选择菜单
                menu = response.payload.get("menu", "")
                print(f"{Colors.BOLD}{Colors.YELLOW}{menu}{Colors.ENDC}")
                
                # 根据语言设置提示符
                if self.current_language == "en":
                    self.current_prompt = "Please select (1/2/3): "
                else:
                    self.current_prompt = "请选择 (1/2/3): "
                
            elif response.type == "input_request":
                # 需要收集用户输入
                system = response.payload.get("system", "")
                missing_fields = response.payload.get("missing_fields", {})
                current_data = response.payload.get("current_data", {})
                error = response.payload.get("error")
                
                print(f"{Colors.YELLOW}📝 {self._get_system_display_name(system)} 需要更多信息{Colors.ENDC}")
                print(f"{Colors.CYAN}" + "=" * 50 + f"{Colors.ENDC}")
                
                if error:
                    print(f"{Colors.RED}❌ {error}{Colors.ENDC}\n")
                
                for field, prompt in missing_fields.items():
                    current_value = current_data.get(field, "")
                    if current_value:
                        print(f"{Colors.GREEN}✓ {field}: {current_value}{Colors.ENDC}")
                    else:
                        print(f"{Colors.YELLOW}○ {prompt}{Colors.ENDC}")
                
                print(f"{Colors.CYAN}" + "=" * 50 + f"{Colors.ENDC}")
                print(f"{Colors.BLUE}💡 请重新输入 '{system}' 并提供完整信息{Colors.ENDC}")
                
            elif response.type == "fortune_response":
                # 显示占卜结果
                result = response.payload.get("result", {})
                reading = result.get("reading", "")
                system = response.payload.get("system", "")
                
                # 使用I18n显示结果标题
                if self.i18n_agent:
                    if system == "bazi":
                        title = self.i18n_agent.get_text("bazi_result_title", self.current_language)
                    elif system == "tarot":
                        title = self.i18n_agent.get_text("tarot_result_title", self.current_language)
                    elif system == "zodiac":
                        title = self.i18n_agent.get_text("zodiac_result_title", self.current_language)
                    else:
                        title = f"🔮 {self._get_system_display_name(system)} 解读结果"
                else:
                    title = f"🔮 {self._get_system_display_name(system)} 解读结果"
                
                print(f"{Colors.CYAN}{title}{Colors.ENDC}")
                print(f"{Colors.YELLOW}" + "=" * 50 + f"{Colors.ENDC}")
                print(f"{reading}")
                print(f"{Colors.YELLOW}" + "=" * 50 + f"{Colors.ENDC}")
                
                # 显示四柱信息（如果是八字）
                if system == "bazi" and "four_pillars" in result:
                    pillars = result["four_pillars"]
                    print(f"\n{Colors.GREEN}📊 四柱八字信息:{Colors.ENDC}")
                    print(f"年柱: {pillars.get('year', '未知')}  月柱: {pillars.get('month', '未知')}")
                    print(f"日柱: {pillars.get('day', '未知')}  时柱: {pillars.get('hour', '未知')}")
                
                # 保存最后的占卜结果用于聊天
                self.last_fortune_reading = {
                    "system": system,
                    "reading": reading,
                    "result": result
                }
                
                # 提供聊天选项
                print(f"\n{Colors.BOLD}{Colors.CYAN}💬 与霄占命理师继续对话{Colors.ENDC}")
                print(f"{Colors.YELLOW}" + "=" * 50 + f"{Colors.ENDC}")
                print(f"{Colors.GREEN}• 直接输入问题开始聊天 (如：我的事业运势如何？){Colors.ENDC}")
                print(f"{Colors.GREEN}• 输入 1/2/3 选择新的占卜系统{Colors.ENDC}")
                print(f"{Colors.GREEN}• 输入 'quit' 退出系统{Colors.ENDC}")
                print(f"{Colors.YELLOW}" + "=" * 50 + f"{Colors.ENDC}")
                
                # 重置提示符，但进入聊天模式
                if self.current_language == "en":
                    self.current_prompt = "💬 Chat or select system: "
                else:
                    self.current_prompt = "💬 聊天或选择系统: "
                self.chat_mode = True
                
            elif response.type == "chat_response":
                # 显示聊天回复
                chat_response = response.payload.get("response", "")
                print(f"{Colors.CYAN}🧙‍♂️ 霄占命理师: {Colors.ENDC}{chat_response}")
                
                # 根据语言设置聊天提示符
                if self.current_language == "en":
                    self.current_prompt = "💬 Continue chat: "
                else:
                    self.current_prompt = "💬 继续聊天: "
                
            else:
                # 显示其他响应
                payload = response.payload or {}
                
                if "routing_info" in payload:
                    routing_info = payload["routing_info"]
                    print(f"{Colors.BLUE}系统响应:{Colors.ENDC}")
                    print(f"  消息类型: {response.type}")
                    print(f"  发送者: {response.sender}")
                    print(f"  语言: {response.language}")
                    print(f"  路由信息: {routing_info}")
                else:
                    print(f"{Colors.BLUE}智能体响应:{Colors.ENDC}")
                    print(f"  {payload}")
            
            print()  # 空行分隔
            
        except Exception as e:
            logger.error(f"Error displaying response: {e}")
            print_error(f"显示响应时出错: {e}")
    
    def _get_system_display_name(self, system_type: str) -> str:
        """获取系统显示名称"""
        system_names = {
            "bazi": "八字命理",
            "tarot": "塔罗占卜", 
            "zodiac": "星座占星",
            "chat": "智能对话"
        }
        return system_names.get(system_type, system_type)
    
    async def shutdown(self) -> None:
        """关闭应用程序"""
        try:
            logger.info("Shutting down application")
            
            # 停止运行时
            if self.runtime:
                await self.runtime.stop()
            
            print(f"{Colors.GREEN}霄占系统已安全关闭。感谢使用！{Colors.ENDC}")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            print_error(f"关闭时出错: {e}")


async def main():
    """主函数"""
    app = FortunetellerStrandsApp()
    await app.run()


def run_strands_cli():
    """CLI 入口点"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"致命错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_strands_cli()