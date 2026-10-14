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

一个终端里跑的命理占卜小工具，把传统占卜系统 + 现代大模型串在一起。流式解读、中英双语、方向键菜单。

## 🌟 功能特色

- **🀄 八字命理** — 传统四柱推命，基于出生年月日时
- **🃏 塔罗牌** — 多种牌阵，抽牌 + 解牌
- **⭐ 西方占星** — 基于生日的星座分析
- **💬 追问对话** — 解读完可以继续深挖（事业、感情、健康、流年……）
- **🌍 中英双语** — 启动选语言，或用 `--lang` 参数
- **⌨️ 方向键菜单** — 非 TTY 环境自动退化为数字输入
- **⚡ 真流式输出** — Token 从大模型直接流出，加载动画覆盖首 token 等待
- **🔌 多家 LLM** — AWS Bedrock (Claude)、Anthropic 直连、OpenAI、DeepSeek

## 🚀 快速开始

```bash
# 1. 克隆
git clone https://github.com/YuchengMaUTK/fortune-teller.git
cd fortune-teller

# 2. 装依赖
python -m venv .venv && source .venv/bin/activate
pip install '.[bedrock]'  # 也可选 openai / deepseek / anthropic / all

# 3. 配置
cp config.yaml.example config.yaml
# 编辑 config.yaml：选一个 provider，填凭证。详见下文。

# 4. 运行
python -m fortune_teller
```

**常用参数：**

```bash
python -m fortune_teller --lang zh        # 跳过语言选择
python -m fortune_teller --system bazi    # 跳过系统选择
python -m fortune_teller --list           # 列出可用占卜系统
python -m fortune_teller --verbose        # 打开控制台日志
```

## 🔧 配置说明

所有配置在 `config.yaml` 里。示例文件列出了所有 provider，选**一个** `llm:` 块即可。

### AWS Bedrock（推荐）

```yaml
llm:
  provider: aws_bedrock
  model: us.anthropic.claude-sonnet-4-5-20250929-v1:0
  region: us-west-2
  temperature: 0.7
  max_tokens: 2000
  # profile: my-profile    # 可选：~/.aws 下的命名 profile
```

凭证走 **boto3 默认解析链**：

1. `config.yaml` 里显式写的 `aws_access_key` / `aws_secret_key`
2. `profile:` 字段指向的命名 AWS profile
3. 环境变量（`AWS_ACCESS_KEY_ID` / `AWS_PROFILE` / …）
4. `~/.aws/credentials` 的 default profile、SSO、IMDS、`credential_process`……

如果 shell 里 `aws sts get-caller-identity` 能跑通，这里就能跑通。

### Anthropic 直连

```yaml
llm:
  provider: anthropic
  model: claude-sonnet-4-5-20250929
```

从 `ANTHROPIC_API_KEY` 读 key。

### OpenAI

```yaml
llm:
  provider: openai
  model: gpt-4o-mini
```

从 `OPENAI_API_KEY` 读 key。

### DeepSeek

```yaml
llm:
  provider: deepseek
  model: deepseek-chat
```

从 `DEEPSEEK_API_KEY` 读 key。

## 🎮 使用流程

1. 选语言（方向键，`q` 退出）
2. 选占卜系统
3. 按提示填信息——生日 / 时间 / 问题 / 牌阵
4. 看解读流式吐出来
5. 读完主解读之后，可以挑一个深入话题再解一次，或者直接跟霄占聊天

## 🏗️ 架构

```
fortune_teller/
├── main.py              # CLI 入口、交互菜单、追问、聊天
├── core/
│   ├── llm_connector.py # 统一 LLM 调度（Bedrock/Anthropic/OpenAI/DeepSeek）
│   ├── aws_connector.py # Bedrock 流式 + 非流式
│   ├── config_manager.py
│   ├── plugin_manager.py
│   └── mock_connector.py
├── plugins/             # 占卜系统（每个自带 prompt 和数据）
│   ├── bazi/
│   ├── tarot/
│   └── zodiac/
├── tools/
│   ├── llm_tool.py      # LLMTool 包装（读 config.yaml）
│   └── mcp_tools.py     # 对包内计算器的 subprocess 封装
├── ui/
│   ├── keyboard_input.py # 方向键菜单，TTY 自适应
│   ├── display.py        # 流式打印、头部、动画
│   └── animation.py
└── i18n/
    └── locales/         # en.json / zh.json
```

`fortune_teller/calculators/` 包含纯 Python 计算器（八字四柱、抽牌、星座判定）；`tools/mcp_tools.py` 通过 subprocess 调用包内模块。仓库根目录的 `mcp/tools/` 保留兼容命令入口。

## 🤝 贡献

见 [CONTRIBUTING.zh.md](CONTRIBUTING.zh.md) — 开发环境、代码规范、新增占卜系统/新语言的指南。

## 📄 许可证

MIT — 详见 [LICENSE](LICENSE)。

## 🙏 致谢

- 传统中国命理智慧
- Anthropic、OpenAI、AWS Bedrock、DeepSeek —— 干真正重活的大模型
- 每一位开 issue 和提 PR 的朋友

---

**古法遇新技，愿你玩得开心。** ✨

## 开发与排盘约定

需要 Python 3.10+。开发环境安装 `pip install '.[dev]'`，离线测试运行 `python -m pytest`。模型 SDK 是可选依赖；`requirements.txt` 保留完整安装方式。

八字 CLI 和插件共用 `lunar_python` 历法：按立春换年、节气换月。输入时间按北京时间（UTC+08:00）解释，日柱午夜换日（sect 2），23 点进入子时；出生地点不参与时区转换或真太阳时校正。海外出生时间请先换算为北京时间。时间未知时暂用中午排年、月、日柱，时柱显示未知，节气当日可能有歧义。

真实模型连接失败会显示错误。离线演示请显式配置 `provider: mock`，输出标记 `[MOCK]`。默认测试不调用付费服务；旧的在线诊断脚本需单独运行。计算器位于 `fortune_teller/calculators/`，`mcp/tools/` 保留旧命令兼容入口。
