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

基于Python的多系统算命程序，使用LLM（大型语言模型）进行解读。

## 功能

- 支持多种算命系统（八字命理、塔罗牌、星座占星等）
- 插件化架构，易于扩展
- 使用LLM提供专业的解读和分析
- 命令行界面，便于使用
- 丰富的视觉呈现，包括彩色输出和表情符号
- 每种占卜系统拥有专属主题和解读领域
- 支持与占卜师聊天模式

## 快速开始

```bash
# 1. 复制配置文件
cp config.yaml.example config.yaml  # 或 cp config.yaml.mock config.yaml 使用模拟模式

# 2. 启动服务
./start_services.sh
```

## 项目结构

```
fortune_teller/
├── core/                       # 核心功能模块
│   ├── __init__.py
│   ├── plugin_manager.py       # 插件管理器
│   ├── base_system.py          # 基础系统接口
│   ├── llm_connector.py        # LLM连接器
│   ├── aws_connector.py        # AWS Bedrock连接器
│   ├── mock_connector.py       # 模拟LLM连接器
│   └── config_manager.py       # 配置管理
├── plugins/                    # 各算命系统插件
│   ├── __init__.py             # 插件注册机制
│   ├── bazi/                   # 八字命理插件
│   ├── tarot/                  # 塔罗牌插件
│   └── zodiac/                 # 星座插件
├── data/                       # 占卜系统数据文件
│   ├── tarot/                  # 塔罗牌数据
│   │   └── cards.json          # 塔罗牌卡牌定义及表情符号
│   ├── bazi/                   # 八字命理数据
│   └── zodiac/                 # 星座占星数据
├── ui/                         # 用户界面
│   ├── __init__.py
│   ├── colors.py               # 终端颜色支持
│   ├── animation.py            # 加载动画
│   └── display.py              # 显示功能
├── utils/                      # 通用工具函数
│   ├── __init__.py
│   └── date_utils.py           # 日期处理工具
├── tests/                      # 测试目录
│   ├── __init__.py
│   └── test_basic_imports.py   # 基本导入测试
└── main.py                     # 主程序
```

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

## 使用方法

### 基础使用

最简单的方式是使用提供的启动脚本：

```bash
./start_services.sh
```

这将启动交互式命令行界面，引导您选择占卜系统并输入必要的信息。

### 命令行选项

您也可以直接使用Python模块并传递命令行参数：

```bash
# 列出可用的占卜系统
python -m fortune_teller.main --list

# 使用特定的占卜系统
python -m fortune_teller.main --system bazi

# 保存解读结果到文件
python -m fortune_teller.main --system tarot --output reading.json

# 显示详细日志（调试模式）
python -m fortune_teller.main --verbose
```

### 占卜系统专属主题

每个占卜系统都有其特有的专属主题，提供针对性的解读：

- **八字命理系统**
  - 🧠 性格命格 - 性格特点、天赋才能和个人品质
  - 💼 事业财运 - 职业发展、财富机遇和谋生方向
  - ❤️ 婚姻情感 - 感情状况、婚姻质量和桃花运势
  - 🧘 健康寿元 - 体质特点、易患疾病和养生之道
  - 🔄 流年大运 - 命运转折、关键时期和吉凶预测

- **塔罗牌系统**
  - 🌟 核心启示 - 牌阵核心信息和主要启示
  - 🚶 当前处境 - 目前面临的状况和心理状态
  - 🧭 阻碍与助力 - 当前面临的挑战和可用资源
  - 🛤️ 潜在路径 - 可能的发展方向和选择建议
  - 💫 精神成长 - 内在成长和个人转变的机会

- **星座占星系统**
  - 🪐 星盘解析 - 整体星盘特点和行星角度
  - 🌠 宫位能量 - 重点宫位和它们的影响
  - 🔄 当前行运 - 现在的行星运行对您的影响
  - 🌈 元素平衡 - 星盘中的元素与能量分布
  - ✨ 星座年运 - 未来一年的星象预测

### 聊天模式

完成基本解读后，您可以选择与霄占命理师进行交互式聊天：

1. 在解读完成后，选择"与霄占聊天"选项
2. 系统会根据您使用的占卜系统，提供专业的聊天体验
3. 您可以询问更多关于解读的问题，或探讨其他命理相关话题
4. 输入"exit"或"退出"返回主菜单

## 环境变量与配置

### LLM服务配置

使用本程序需要根据选择的LLM提供商设置相应的环境变量：

- **OpenAI**:
  - `OPENAI_API_KEY`: OpenAI API密钥

- **Anthropic直连**:
  - `ANTHROPIC_API_KEY`: Anthropic API密钥

- **AWS Bedrock**:
  - `AWS_ACCESS_KEY_ID`: AWS访问密钥ID
  - `AWS_SECRET_ACCESS_KEY`: AWS私有访问密钥
  - `AWS_REGION`: AWS区域（如us-east-1）

### 测试模式（无需API密钥）

如果您只想测试系统功能而不需要真实的LLM响应，可以使用Mock模式：

```bash
# 复制Mock配置文件
cp config.yaml.mock config.yaml

# 运行程序
python -m fortune_teller.main
```

Mock模式下系统将使用预设的模拟响应，无需任何API密钥。

## 扩展新系统

要添加新的算命系统，只需:

1. 在`plugins/`下创建新目录
2. 实现继承自`BaseFortuneSystem`的系统类
3. 创建`manifest.yaml`描述插件
4. 在`__init__.py`中注册插件

有关详细步骤，请参阅[贡献指南](CONTRIBUTING.md)。

## 文档

本项目包含以下文档：

- [安装指南](INSTALL.md) - 详细的安装和配置说明
- [贡献指南](CONTRIBUTING.md) - 如何为项目做出贡献
- [行为准则](CODE_OF_CONDUCT.md) - 参与项目的行为规范
- [LLM设置指南](LLM_SETUP_GUIDE.md) - 详细的LLM配置指南

## 故障排除

如果在使用过程中遇到问题：

1. 检查配置文件是否正确设置
2. 确认环境变量是否正确配置
3. 查看`fortune_teller.log`日志文件
4. 使用以下工具诊断LLM连接问题：
   ```bash
   python troubleshoot_llm.py
   ```

## 贡献

欢迎贡献代码、报告问题或提出改进建议！请查看[贡献指南](CONTRIBUTING.md)了解更多信息。

## 许可证

本项目采用[MIT许可证](LICENSE)。

## 开发路线图

### 计划中的功能

- **支持DeepSeek** - 增加对DeepSeek等其他大型语言模型的支持
- **新的占卜系统**
  - 紫微斗数 - 中国传统命理学，基于出生时间与星宿组合
  - 易经六爻 - 基于《易经》的占卜方法
  - 奇门遁甲 - 中国古代预测学的重要分支
- **多语言支持** - 添加英文等其他语言界面
- **改进用户界面**
  - 网页前端界面
  - 桌面GUI应用程序
  - 移动友好型界面
- **更丰富的可视化**
  - 八字命盘图形化展示
  - 塔罗牌牌阵视觉呈现
  - 星盘图生成与解读

### 参与贡献

我们欢迎社区贡献以上任何功能！如有兴趣，请参阅[贡献指南](CONTRIBUTING.md)了解如何参与。
