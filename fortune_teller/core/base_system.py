"""
Base system interface for fortune telling plugins.
All fortune telling plugins must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseFortuneSystem(ABC):
    """Base abstract class for all fortune telling systems."""
    
    def __init__(self, name: str, display_name: str, description: str = ""):
        """
        Initialize the fortune system.
        
        Args:
            name: Unique identifier for the system
            display_name: User-friendly name for display
            description: Brief description of the fortune system
        """
        self.name = name
        self.display_name = display_name
        self.description = description
    
    @abstractmethod
    def validate_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input for this fortune system.
        
        Args:
            user_input: Dictionary containing user input data
            
        Returns:
            Validated and possibly normalized input data
            
        Raises:
            ValueError: If the input data is invalid
        """
        pass
    
    @abstractmethod
    def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the validated input data according to the fortune system's rules.
        
        Args:
            validated_input: Validated user input
            
        Returns:
            Processed data ready for LLM prompt generation
        """
        pass
    
    @abstractmethod
    def generate_llm_prompt(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate prompts for the LLM based on processed data.
        
        Args:
            processed_data: Data processed by the fortune system
            
        Returns:
            Dictionary containing system_prompt and user_prompt for the LLM
        """
        pass
    
    @abstractmethod
    def format_result(self, llm_response: str) -> Dict[str, Any]:
        """
        Format the LLM response into structured output.
        
        Args:
            llm_response: Raw response from the LLM
            
        Returns:
            Formatted and structured result
        """
        pass
    
    def get_required_inputs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about required inputs for this fortune system.
        
        Returns:
            Dictionary mapping input field names to their metadata
            (e.g., type, description, validation rules)
        """
        # Can be overridden by subclasses to provide more specific input requirements
        return {}

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get general information about this fortune system.
        
        Returns:
            Dictionary containing system metadata
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "required_inputs": self.get_required_inputs()
        }
    
    def display_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """
        Display processed data in a system-specific format.
        
        Args:
            processed_data: Data processed by the fortune system
        """
        # Default implementation just prints the data
        print(f"\n处理结果: {processed_data}")
    
    def get_chat_system_prompt(self) -> str:
        """
        Get a system prompt for chat mode specific to this fortune system.
        
        Returns:
            System prompt string for chat mode
        """
        # Default chat system prompt
        return f"""你是"霄占"命理大师，一位来自中国的传统命理学专家，已有30年的占卜经验，性格风趣幽默又不失智慧。
现在你正在与求测者进行轻松的聊天互动。你可以谈论命理学知识、回答关于运势的问题，
也可以聊一些日常话题，但始终保持着命理师的角色和视角。
用生动有趣的语言表达，偶尔引用古诗词或俏皮话，让谈话充满趣味性。
让求测者感觉是在和一位睿智而亲切的老朋友聊天。

对话应简洁精炼，回答控制在200字以内，保持幽默风趣的语气。"""
