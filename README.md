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

A modern, AI-powered fortune telling application supporting multiple divination systems with streaming responses and intuitive keyboard navigation.

## 🌟 Features

- **🀄 BaZi (八字命理)** - Traditional Chinese fortune telling based on birth date and time
- **🃏 Tarot Cards** - Classic tarot card readings with multiple spreads
- **⭐ Western Astrology** - Zodiac-based fortune analysis
- **🌍 Bilingual Support** - English and Chinese with professional i18n system
- **⌨️ Modern Interface** - Smooth keyboard navigation with arrow keys
- **⚡ Real-time Streaming** - Watch your reading appear word by word
- **🎯 MCP Integration** - Accurate calculations using Model Context Protocol tools

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/fortune-teller.git
cd fortune-teller

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy configuration
cp config.yaml.example config.yaml  # For real LLM
# OR
cp config.yaml.mock config.yaml     # For testing without API keys

# 4. Run the application
python -m fortune_teller.simple_main
```

## 🎮 Usage

1. **Language Selection** - Use arrow keys to choose English or Chinese
2. **System Selection** - Pick your preferred divination method
3. **Input Information** - Provide birth details or questions as needed
4. **Watch Reading Generate** - See your fortune appear in real-time
5. **Interactive Navigation** - Smooth, modern interface throughout

## 🏗️ Architecture

### Core Components

- **🧠 AI Agents** - Specialized agents for each fortune telling system
- **🔧 MCP Tools** - Accurate calculations for BaZi, Tarot, and Zodiac
- **🌍 I18n System** - Clean, JSON-based internationalization
- **🎨 UI Components** - Modern keyboard navigation and streaming output
- **⚙️ LLM Integration** - Support for AWS Bedrock, OpenAI, and Anthropic

### Project Structure

```
fortune_teller/
├── agents/                 # Fortune telling agents
│   ├── bazi_agent.py      # BaZi fortune telling
│   ├── tarot_agent.py     # Tarot card reading
│   └── zodiac_agent.py    # Western astrology
├── tools/                  # Core tools
│   ├── llm_tool.py        # LLM integration with streaming
│   └── mcp_tool.py        # Model Context Protocol tools
├── mcp/                    # MCP tool implementations
│   └── tools/             # BaZi, Tarot, Zodiac converters
├── i18n/                   # Internationalization
│   └── locales/           # English and Chinese translations
├── ui/                     # User interface
│   ├── keyboard_input.py  # Arrow key navigation
│   └── colors.py          # Terminal styling
└── simple_main.py         # Clean main application
```

## 🔧 Configuration

### LLM Providers

Choose your preferred LLM provider by setting environment variables:

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

### Mock Mode (No API Keys Required)

For testing without LLM services:
```bash
cp config.yaml.mock config.yaml
python -m fortune_teller.simple_main
```

## 🌍 Internationalization

The application supports English and Chinese with a clean i18n system:

```python
from fortune_teller.i18n import t

# Get translated text
title = t("welcome_title", "en")  # "Welcome to Fortune Teller"
title = t("welcome_title", "zh")  # "欢迎使用霄占"
```

Adding new languages is simple - just add a new JSON file in `i18n/locales/`.

## 🎯 MCP Tools

Accurate fortune telling calculations powered by Model Context Protocol:

- **BaZi Converter** - Precise four pillars calculation
- **Tarot Converter** - Card drawing and interpretation
- **Zodiac Converter** - Astrological sign determination

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Traditional Chinese fortune telling wisdom
- Modern AI and LLM technologies
- The open source community

---

**Experience the fusion of ancient wisdom and modern technology with 霄占 Fortune Teller!** ✨
