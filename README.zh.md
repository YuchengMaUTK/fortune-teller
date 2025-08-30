# 霄占 (Fortune Teller)

```
██╗  ██╗██╗ █████╗  ██████╗      ███████╗██╗  ██╗ █████╗ ███╗   ██╗
╚██╗██╔╝██║██╔══██╗██╔═══██╗     ╚══███╔╝██║  ██║██╔══██╗████╗  ██║
 ╚███╔╝ ██║███████║██║   ██║       ███╔╝ ███████║███████║██╔██╗ ██║
 ██╔██╗ ██║██╔══██║██║   ██║      ███╔╝  ██╔══██║██╔══██║██║╚██╗██║
██╔╝ ██╗██║██║  ██║╚██████╔╝     ███████╗██║  ██║██║  ██║██║ ╚████║
╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝      ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
```

> ✨ 古今命理，尽在掌握 ✨

**[English](README.md) | 中文**

现代化的AI驱动占卜应用，支持多种占卜系统，具备流式响应和直观的键盘导航功能。

## 🌟 功能特色

- **🀄 八字命理** - 基于出生年月日时的传统中国命理分析
- **🃏 塔罗牌** - 经典塔罗牌占卜，支持多种牌阵
- **⭐ 西方占星** - 基于星座的命运分析
- **🌍 双语支持** - 专业的中英文国际化系统
- **⌨️ 现代界面** - 流畅的方向键导航
- **⚡ 实时流式输出** - 观看占卜结果逐字显现
- **🎯 MCP集成** - 使用模型上下文协议工具进行精确计算

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/YuchengMaUTK/fortune-teller.git
cd fortune-teller

# 2. 安装依赖
pip install -r requirements.txt

# 3. 复制配置文件
cp config.yaml.example config.yaml  # 使用真实LLM
# 或者
cp config.yaml.mock config.yaml     # 测试模式，无需API密钥

# 4. 运行应用
python -m fortune_teller
```

## 🎮 使用方法

1. **语言选择** - 使用方向键选择中文或英文
2. **系统选择** - 选择您偏好的占卜方法
3. **输入信息** - 根据需要提供出生信息或问题
4. **观看生成过程** - 实时观看占卜结果生成
5. **交互导航** - 全程流畅的现代化界面

## 🏗️ 架构设计

### 核心组件

- **🧠 AI智能体** - 各占卜系统的专业智能体
- **🔧 MCP工具** - 八字、塔罗、星座的精确计算
- **🌍 国际化系统** - 基于JSON的清洁国际化方案
- **🎨 UI组件** - 现代键盘导航和流式输出
- **⚙️ LLM集成** - 支持AWS Bedrock、OpenAI和Anthropic

### 项目结构

```
fortune_teller/
├── agents/                 # 占卜智能体
│   ├── bazi_agent.py      # 八字命理
│   ├── tarot_agent.py     # 塔罗牌占卜
│   └── zodiac_agent.py    # 西方占星
├── tools/                  # 核心工具
│   ├── llm_tool.py        # 带流式输出的LLM集成
│   └── mcp_tool.py        # 模型上下文协议工具
├── mcp/                    # MCP工具实现
│   └── tools/             # 八字、塔罗、星座转换器
├── i18n/                   # 国际化
│   └── locales/           # 中英文翻译文件
├── ui/                     # 用户界面
│   ├── keyboard_input.py  # 方向键导航
│   └── colors.py          # 终端样式
└── simple_main.py         # 清洁的主应用程序
```

## 🔧 配置说明

### LLM服务商

通过设置环境变量选择您偏好的LLM服务商：

**AWS Bedrock:**
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

**OpenAI:**
```bash
export OPENAI_API_KEY=your_key
```

**Anthropic:**
```bash
export ANTHROPIC_API_KEY=your_key
```

### 模拟模式（无需API密钥）

测试时无需LLM服务：
```bash
cp config.yaml.mock config.yaml
python -m fortune_teller
```

## 🌍 国际化

应用支持中英文，采用清洁的i18n系统：

```python
from fortune_teller.i18n import t

# 获取翻译文本
title = t("welcome_title", "en")  # "Welcome to Fortune Teller"
title = t("welcome_title", "zh")  # "欢迎使用霄占"
```

添加新语言很简单 - 只需在 `i18n/locales/` 中添加新的JSON文件。

## 🎯 MCP工具

基于模型上下文协议的精确占卜计算：

- **八字转换器** - 精确的四柱计算
- **塔罗转换器** - 抽牌和解读
- **星座转换器** - 星座判定

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 传统中国命理学智慧
- 现代AI和LLM技术
- 开源社区

---

**体验古老智慧与现代科技的完美融合！** ✨
