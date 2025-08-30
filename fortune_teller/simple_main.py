#!/usr/bin/env python3
"""
Simple Fortune Teller - Clean, minimal implementation
"""

import asyncio
import datetime
from typing import Optional
from .ui.colors import Colors
from .ui.keyboard_input import select_language, select_gender, select_fortune_system
from .i18n import t


class SimpleFortuneTeller:
    """Simple, clean fortune telling application"""
    
    def __init__(self):
        self.language = "zh"
    
    async def run(self):
        """Main application loop"""
        self.show_welcome()
        
        # Language selection
        self.language = await self.select_language()
        if not self.language:
            return
        
        # System selection  
        system = await self.select_system()
        if not system:
            return
        
        # Get user data and generate reading
        if system == "bazi":
            await self.run_bazi()
        elif system == "tarot":
            await self.run_tarot()
        elif system == "zodiac":
            await self.run_zodiac()
    
    def show_welcome(self):
        """Show welcome screen"""
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
        print(f"{Colors.BOLD}{Colors.YELLOW}{t('welcome_title', 'en')} / {t('welcome_title', 'zh')}{Colors.ENDC}")
        print(f"{Colors.CYAN}✨ {t('welcome_subtitle', 'en')} / {t('welcome_subtitle', 'zh')} ✨{Colors.ENDC}")
        print("\n" + "=" * 80 + "\n")
    
    async def select_language(self) -> Optional[str]:
        """Language selection with keyboard navigation"""
        try:
            return select_language()
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}{t('status_cancelled', 'zh')}{Colors.ENDC}")
            return None
    
    async def select_system(self) -> Optional[str]:
        """System selection with keyboard navigation"""
        try:
            return select_fortune_system(self.language)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}{t('status_cancelled', self.language)}{Colors.ENDC}")
            return None
    
    async def run_bazi(self):
        """Run BaZi fortune telling"""
        print(f"{Colors.CYAN}🀄 {t('system_bazi', self.language)}{Colors.ENDC}\n")
        
        # Get birth info
        birth_date = self.get_birth_date()
        if not birth_date:
            return
        
        birth_time = self.get_birth_time()
        if not birth_time:
            return
        
        gender = select_gender(self.language)
        if not gender:
            return
        
        # Calculate BaZi using MCP tool
        from .tools.mcp_tool import MCPTool
        mcp = MCPTool()
        
        try:
            bazi_result = await mcp.invoke_tool(
                "bazi_converter",
                "convert",
                [birth_date.year, birth_date.month, birth_date.day, birth_time.hour]
            )
            
            # Generate reading with LLM
            await self.generate_bazi_reading(bazi_result, birth_date, birth_time, gender)
            
        except Exception as e:
            print(f"{Colors.RED}❌ {t('error_llm_unavailable', self.language)}: {e}{Colors.ENDC}")
    
    async def run_tarot(self):
        """Run Tarot reading"""
        print(f"{Colors.CYAN}🃏 {t('system_tarot', self.language)}{Colors.ENDC}\n")
        
        # Get question
        question = input(f"{t('input_question', self.language)} ")
        if not question.strip():
            return
        
        # Select spread (simplified - just use single card for now)
        from .tools.mcp_tool import MCPTool
        mcp = MCPTool()
        
        try:
            tarot_result = await mcp.invoke_tool("tarot_converter", "draw_cards", [1])
            await self.generate_tarot_reading(tarot_result, question)
        except Exception as e:
            print(f"{Colors.RED}❌ {t('error_llm_unavailable', self.language)}: {e}{Colors.ENDC}")
    
    async def run_zodiac(self):
        """Run Zodiac reading"""
        print(f"{Colors.CYAN}⭐ {t('system_zodiac', self.language)}{Colors.ENDC}\n")
        
        # Get birth date
        birth_date = self.get_birth_date()
        if not birth_date:
            return
        
        # Calculate zodiac using MCP tool
        from .tools.mcp_tool import MCPTool
        mcp = MCPTool()
        
        try:
            zodiac_result = await mcp.invoke_tool(
                "zodiac_converter", 
                "convert",
                [birth_date.year, birth_date.month, birth_date.day]
            )
            
            await self.generate_zodiac_reading(zodiac_result, birth_date)
            
        except Exception as e:
            print(f"{Colors.RED}❌ {t('error_llm_unavailable', self.language)}: {e}{Colors.ENDC}")
    
    def get_birth_date(self) -> Optional[datetime.date]:
        """Get birth date from user"""
        while True:
            try:
                date_str = input(f"{t('input_birth_date', self.language)} ")
                if not date_str.strip():
                    return None
                
                year, month, day = map(int, date_str.split('-'))
                return datetime.date(year, month, day)
                
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}{t('error_invalid_date', self.language)}{Colors.ENDC}")
                return None
    
    def get_birth_time(self) -> Optional[datetime.time]:
        """Get birth time from user"""
        while True:
            try:
                time_str = input(f"{t('input_birth_time', self.language)} ")
                if not time_str.strip():
                    return None
                
                hour, minute = map(int, time_str.split(':'))
                return datetime.time(hour, minute)
                
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}{t('error_invalid_time', self.language)}{Colors.ENDC}")
                return None
    
    async def generate_bazi_reading(self, bazi_result, birth_date, birth_time, gender):
        """Generate BaZi reading with streaming"""
        from .tools.llm_tool import LLMTool
        
        llm = LLMTool()
        
        system_prompt = "你是一位经验丰富的八字命理师，精通传统命理学。" if self.language == "zh" else "You are an experienced BaZi fortune teller."
        
        user_prompt = f"""
请分析以下八字信息：
出生日期：{birth_date}
出生时间：{birth_time}
性别：{gender}
八字：{bazi_result.get('four_pillars', '')}
日主：{bazi_result.get('day_master', '')}
五行：{bazi_result.get('elements', {})}

请提供性格特点和运势建议。
""" if self.language == "zh" else f"""
Please analyze the following BaZi information:
Birth Date: {birth_date}
Birth Time: {birth_time}
Gender: {gender}
Four Pillars: {bazi_result.get('four_pillars', '')}
Day Master: {bazi_result.get('day_master', '')}
Elements: {bazi_result.get('elements', {})}

Please provide personality traits and fortune advice.
"""
        
        print(f"\n{Colors.CYAN}🔮 {t('generating_reading', self.language)}{Colors.ENDC}\n")
        
        reading = await llm.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            language=self.language,
            stream=True
        )
        
        print(f"\n\n{Colors.GREEN}✅ {t('reading_complete', self.language)}{Colors.ENDC}")
    
    async def generate_tarot_reading(self, tarot_result, question):
        """Generate Tarot reading with streaming"""
        from .tools.llm_tool import LLMTool
        
        llm = LLMTool()
        
        system_prompt = "你是一位专业的塔罗牌占卜师。" if self.language == "zh" else "You are a professional tarot card reader."
        
        cards = tarot_result.get('cards', [])
        card_info = cards[0] if cards else {}
        
        user_prompt = f"""
问题：{question}
抽到的牌：{card_info.get('name', '')} {card_info.get('emoji', '')}
牌义：{card_info.get('meaning', '')}
正逆位：{card_info.get('orientation', '')}

请解读这张牌对问题的指导意义。
""" if self.language == "zh" else f"""
Question: {question}
Card drawn: {card_info.get('name', '')} {card_info.get('emoji', '')}
Meaning: {card_info.get('meaning', '')}
Orientation: {card_info.get('orientation', '')}

Please interpret this card's guidance for the question.
"""
        
        print(f"\n{Colors.CYAN}🔮 {t('generating_reading', self.language)}{Colors.ENDC}\n")
        
        reading = await llm.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            language=self.language,
            stream=True
        )
        
        print(f"\n\n{Colors.GREEN}✅ {t('reading_complete', self.language)}{Colors.ENDC}")
    
    async def generate_zodiac_reading(self, zodiac_result, birth_date):
        """Generate Zodiac reading with streaming"""
        from .tools.llm_tool import LLMTool
        
        llm = LLMTool()
        
        system_prompt = "你是一位专业的占星师，精通西方占星学。" if self.language == "zh" else "You are a professional astrologer."
        
        zodiac_sign = zodiac_result.get('zodiac_sign', {})
        
        user_prompt = f"""
出生日期：{birth_date}
星座：{zodiac_sign.get('name', '')} {zodiac_sign.get('emoji', '')}
元素：{zodiac_sign.get('element', '')}

请分析这个星座的性格特点和运势。
""" if self.language == "zh" else f"""
Birth Date: {birth_date}
Zodiac Sign: {zodiac_sign.get('name', '')} {zodiac_sign.get('emoji', '')}
Element: {zodiac_sign.get('element', '')}

Please analyze the personality traits and fortune of this zodiac sign.
"""
        
        print(f"\n{Colors.CYAN}🔮 {t('generating_reading', self.language)}{Colors.ENDC}\n")
        
        reading = await llm.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            language=self.language,
            stream=True
        )
        
        print(f"\n\n{Colors.GREEN}✅ {t('reading_complete', self.language)}{Colors.ENDC}")


async def main():
    """Main entry point"""
    app = SimpleFortuneTeller()
    try:
        await app.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}{t('status_goodbye', 'zh')}{Colors.ENDC}")


if __name__ == "__main__":
    asyncio.run(main())
