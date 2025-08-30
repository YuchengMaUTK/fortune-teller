# Contributing to Fortune Teller

**English | [中文](CONTRIBUTING.zh.md)**

Thank you for your interest in contributing to Fortune Teller! This document provides guidelines for contributing to our modern, AI-powered fortune telling application.

## 🌟 Project Overview

Fortune Teller is a clean, modern application featuring:
- **🌍 Bilingual support** (English/Chinese) with professional i18n
- **⌨️ Modern keyboard navigation** with smooth arrow key controls
- **⚡ Real-time streaming** LLM responses
- **🎯 Accurate calculations** via MCP (Model Context Protocol) tools
- **🎨 Professional terminal UI** with colors and animations

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- One of the following LLM providers:
  - AWS Bedrock (recommended)
  - OpenAI API
  - Anthropic API

### Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/yourusername/fortune-teller.git
cd fortune-teller

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up configuration
cp config.yaml.mock config.yaml  # For testing without API keys
# OR
cp config.yaml.example config.yaml  # Configure with your LLM provider

# 5. Run the application
python -m fortune_teller
```

## 🏗️ Architecture

### Core Components

```
fortune_teller/
├── simple_main.py          # Clean main application
├── i18n/                   # Internationalization system
│   └── locales/           # Translation files (en.json, zh.json)
├── ui/                     # User interface components
│   ├── keyboard_input.py  # Arrow key navigation
│   └── colors.py          # Terminal styling
├── tools/                  # Core functionality
│   ├── llm_tool.py        # LLM integration with streaming
│   └── mcp_tool.py        # Model Context Protocol tools
└── mcp/tools/             # Fortune telling calculations
    ├── bazi_converter.py  # Chinese BaZi calculations
    ├── tarot_picker.py    # Tarot card selection
    └── zodiac_converter.py # Western astrology
```

## 🤝 How to Contribute

### 1. **Bug Reports**

When reporting bugs, please include:
- **Environment**: OS, Python version, LLM provider
- **Steps to reproduce**: Clear, numbered steps
- **Expected vs actual behavior**
- **Error messages**: Full stack traces if available
- **Configuration**: Sanitized config (remove API keys)

### 2. **Feature Requests**

For new features, please:
- **Check existing issues** to avoid duplicates
- **Describe the use case** and user benefit
- **Consider internationalization** (English/Chinese support)
- **Think about UI/UX** impact on keyboard navigation

### 3. **Code Contributions**

#### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow our coding standards**:
   - Clean, readable code with meaningful names
   - Proper error handling and logging
   - Support for both English and Chinese
   - Maintain keyboard navigation compatibility

3. **Test your changes**:
   ```bash
   # Test basic functionality
   python -m fortune_teller
   
   # Test i18n system
   python -c "from fortune_teller.i18n import t; print(t('welcome_title', 'en'))"
   
   # Test keyboard navigation (interactive)
   python tests/test_keyboard.py
   ```

4. **Update documentation**:
   - Update both README.md and README.zh.md if needed
   - Add/update translation keys in i18n/locales/
   - Document new configuration options

5. **Submit pull request**:
   - Clear title and description
   - Reference related issues
   - Include screenshots for UI changes

#### Code Style Guidelines

- **Python**: Follow PEP 8, use meaningful variable names
- **Async/await**: Use for LLM calls and I/O operations
- **Error handling**: Graceful degradation, user-friendly messages
- **Internationalization**: All user-facing text must use i18n system
- **Comments**: Explain complex logic, especially fortune telling algorithms

### 4. **Adding New Fortune Systems**

To add a new divination system (e.g., I Ching, Numerology):

1. **Create MCP tool**:
   ```python
   # mcp/tools/new_system_converter.py
   #!/usr/bin/env python3
   """New fortune system calculations"""
   
   def calculate_fortune(birth_date, additional_params):
       """Calculate fortune using new system"""
       # Implementation here
       return {"result": "fortune_data"}
   ```

2. **Add translations**:
   ```json
   // i18n/locales/en.json
   {
     "system_new": "New Fortune System",
     "system_new_desc": "Description of the new system"
   }
   
   // i18n/locales/zh.json  
   {
     "system_new": "新占卜系统",
     "system_new_desc": "新系统的描述"
   }
   ```

3. **Update UI**:
   ```python
   # Add to ui/keyboard_input.py select_fortune_system()
   options.append(f"🔮 {t('system_new', language)} - {t('system_new_desc', language)}")
   ```

4. **Implement in main app**:
   ```python
   # Add to simple_main.py
   async def run_new_system(self):
       """Run new fortune system"""
       # Implementation here
   ```

### 5. **Internationalization (i18n)**

When adding new text:

1. **Never hardcode strings**:
   ```python
   # ❌ Bad
   print("Welcome to Fortune Teller")
   
   # ✅ Good
   from fortune_teller.i18n import t
   print(t("welcome_title", language))
   ```

2. **Add to both language files**:
   ```json
   // en.json
   {"new_feature_title": "New Feature"}
   
   // zh.json  
   {"new_feature_title": "新功能"}
   ```

3. **Use descriptive keys**:
   ```python
   # ✅ Good key names
   t("error_invalid_date", lang)
   t("system_bazi_desc", lang)
   t("navigation_arrows", lang)
   ```

## 🧪 Testing

### Manual Testing

```bash
# Test language switching
python -m fortune_teller

# Test streaming output
python tests/test_simple_streaming.py

# Test i18n system
python tests/test_i18n_complete.py
```

### Automated Testing

```bash
# Run all tests
python -m pytest tests/

# Test specific component
python -m pytest tests/test_i18n_complete.py -v
```

## 📋 Development Guidelines

### Commit Messages

Use conventional commits with emojis:

```bash
# Features
git commit -m "✨ Add new tarot spread selection"

# Bug fixes  
git commit -m "🐛 Fix keyboard navigation on Windows"

# Documentation
git commit -m "📚 Update installation instructions"

# Internationalization
git commit -m "🌍 Add Spanish translation support"

# Refactoring
git commit -m "♻️ Simplify LLM tool initialization"
```

### Branch Naming

- `feature/add-numerology-system`
- `bugfix/keyboard-navigation-windows`
- `docs/update-contributing-guide`
- `i18n/add-spanish-support`

## 🎯 Priority Areas

We especially welcome contributions in:

1. **🌍 New Languages**: Spanish, French, Japanese translations
2. **🔮 Fortune Systems**: I Ching, Numerology, Runes
3. **🎨 UI Improvements**: Better animations, progress indicators
4. **🧪 Testing**: Automated tests, edge case handling
5. **📱 Platform Support**: Windows compatibility, mobile-friendly output
6. **⚡ Performance**: Faster LLM responses, caching

## 🆘 Getting Help

- **💬 Discussions**: Use GitHub Discussions for questions
- **🐛 Issues**: Report bugs via GitHub Issues
- **📧 Contact**: Reach out to maintainers for complex contributions

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make Fortune Teller better for everyone!** ✨
