#!/usr/bin/env python3
"""
Setup script for Fortune Teller package.
"""
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if not line.startswith("#")]

with open("README.md", "w") as f:
    f.write("""# Fortune Teller

基于Python的多系统算命程序，使用LLM（大型语言模型）进行解读。

## 功能

- 支持多种算命系统（八字命理、塔罗牌、星座占星等）
- 插件化架构，易于扩展
- 使用LLM提供专业的解读和分析
- 命令行界面，便于使用

## 安装

```bash
pip install -e .
```

## 使用方法

```bash
# 列出可用的占卜系统
python -m fortune_teller.main --list

# 使用特定的占卜系统
python -m fortune_teller.main --system bazi

# 保存解读结果到文件
python -m fortune_teller.main --system tarot --output reading.json
```

## 环境变量

- `OPENAI_API_KEY`: OpenAI API密钥（使用OpenAI LLM时需要）
- `ANTHROPIC_API_KEY`: Anthropic API密钥（使用Claude时需要）
""")

setup(
    name="fortune_teller",
    version="0.1.0",
    description="基于LLM的多系统算命程序",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Fortune Teller Team",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "fortune-teller=fortune_teller.main:run_cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
