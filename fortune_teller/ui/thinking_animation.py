"""
聊天思考动画模块，为聊天流式输出提供更好的用户体验
"""
import sys
import time
import threading
from fortune_teller.ui.colors import Colors

class ChatThinkingAnimation:
    """
    聊天思考动画，适用于聊天界面的轻量级动画。
    在等待大模型首个响应块时显示思考动画，提供即时视觉反馈。
    """
    
    def __init__(self, prefix=None):
        """
        初始化聊天思考动画
        
        Args:
            prefix: 动画前的文字，默认为带颜色的"霄占:"
        """
        self.prefix = prefix or f"{Colors.GREEN}霄占: {Colors.ENDC}{Colors.CYAN}"
        self.suffix = f"{Colors.ENDC}"
        self.thinking_frames = ["思考中", "思考中.", "思考中..", "思考中..."]
        self.running = False
        self.thread = None
        self._stop_event = threading.Event()
        
    def start(self):
        """启动思考动画"""
        if not self.running:
            self.running = True
            self._stop_event.clear()
            self.thread = threading.Thread(target=self._animate)
            self.thread.daemon = True  # 让线程在主程序退出时自动结束
            self.thread.start()
        
    def stop(self):
        """
        停止思考动画并清除
        在收到首个响应块时调用此方法以无缝过渡到实际内容
        """
        if self.running:
            self.running = False
            self._stop_event.set()
            if self.thread:
                self.thread.join(timeout=0.5)
                
            # 清除动画文本（回到行首并清除整行）
            sys.stdout.write("\r" + " " * 50 + "\r")
            sys.stdout.flush()
            
            # 重新打印前缀，为实际内容做准备
            sys.stdout.write(f"{Colors.GREEN}霄占: {Colors.ENDC}")
            sys.stdout.flush()
        
    def _animate(self):
        """动画循环，显示不同的思考帧"""
        i = 0
        try:
            while self.running and not self._stop_event.is_set():
                frame = self.thinking_frames[i % len(self.thinking_frames)]
                # 清除当前行并显示新帧
                sys.stdout.write(f"\r{self.prefix}{frame}{self.suffix}")
                sys.stdout.flush()
                i += 1
                # 使用事件等待，这样可以更快地响应停止请求
                # 保持较慢的动画速度以匹配整体流畅的体验
                self._stop_event.wait(0.4)  # 增加从0.3秒到0.4秒，使动画更加平缓
        except Exception as e:
            import logging
            logging.getLogger("ChatThinkingAnimation").error(f"动画线程错误: {e}")
