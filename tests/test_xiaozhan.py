#!/usr/bin/env python3
"""
霄占用户测试脚本
Test script for Xiaozhan fortune telling system
"""

import subprocess
import sys
from pathlib import Path

def test_original_version():
    """测试原版霄占"""
    print("🔮 测试原版霄占 (Original Xiaozhan)")
    print("=" * 50)
    print("运行命令: python -m fortune_teller.main")
    print("提示: 选择占卜系统后按照提示输入信息")
    print("退出: 在任何输入提示时输入 'quit' 或按 Ctrl+C")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "fortune_teller.main"], 
                      cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n✅ 测试完成")

def test_strands_version():
    """测试 Strands Agents 版本"""
    print("🤖 测试 Strands Agents 版本")
    print("=" * 50)
    print("运行命令: python -m fortune_teller.strands_main")
    print("提示: 这是新的多智能体架构版本")
    print("退出: 输入 'quit' 或按 Ctrl+C")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "fortune_teller.strands_main"], 
                      cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n✅ 测试完成")

def main():
    """主测试菜单"""
    print("🌟 霄占 (Xiaozhan) 用户测试")
    print("=" * 50)
    print("1. 测试原版霄占 (传统版本)")
    print("2. 测试 Strands Agents 版本 (新架构)")
    print("3. 退出")
    print()
    
    while True:
        try:
            choice = input("请选择测试版本 (1-3): ").strip()
            
            if choice == "1":
                test_original_version()
            elif choice == "2":
                test_strands_version()
            elif choice == "3":
                print("👋 再见！")
                break
            else:
                print("❌ 请输入有效选项 (1-3)")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break

if __name__ == "__main__":
    main()
