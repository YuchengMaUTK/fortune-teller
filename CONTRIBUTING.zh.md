# 贡献指南

**[English](CONTRIBUTING.md) | 中文**

感谢您对霄占项目的贡献兴趣！本文档为我们现代化的AI驱动占卜应用提供贡献指南。

## 🌟 项目概览

霄占是一个简洁、现代的应用程序，具有以下特色：
- **🌍 双语支持** (中英文) 专业国际化系统
- **⌨️ 现代键盘导航** 流畅的方向键控制
- **⚡ 实时流式输出** LLM响应
- **🎯 精确计算** 通过MCP (模型上下文协议) 工具
- **🎨 专业终端界面** 带颜色和动画

## 🚀 开始使用

### 前置要求

- Python 3.8+
- Git
- 以下LLM服务商之一：
  - AWS Bedrock (推荐)
  - OpenAI API
  - Anthropic API

### 开发环境设置

```bash
# 1. Fork并克隆仓库
git clone https://github.com/yourusername/fortune-teller.git
cd fortune-teller

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 设置配置
cp config.yaml.mock config.yaml  # 测试模式，无需API密钥
# 或者
cp config.yaml.example config.yaml  # 配置您的LLM服务商

# 5. 运行应用
python -m fortune_teller
```

## 🏗️ 架构设计

### 核心组件

```
fortune_teller/
├── simple_main.py          # 简洁的主应用程序
├── i18n/                   # 国际化系统
│   └── locales/           # 翻译文件 (en.json, zh.json)
├── ui/                     # 用户界面组件
│   ├── keyboard_input.py  # 方向键导航
│   └── colors.py          # 终端样式
├── tools/                  # 核心功能
│   ├── llm_tool.py        # 带流式输出的LLM集成
│   └── mcp_tool.py        # 模型上下文协议工具
└── mcp/tools/             # 占卜计算
    ├── bazi_converter.py  # 中国八字计算
    ├── tarot_picker.py    # 塔罗牌选择
    └── zodiac_converter.py # 西方占星
```

## 🤝 如何贡献

### 1. **Bug报告**

报告Bug时，请包含：
- **环境信息**: 操作系统、Python版本、LLM服务商
- **重现步骤**: 清晰的编号步骤
- **预期与实际行为**
- **错误信息**: 完整的堆栈跟踪（如有）
- **配置**: 清理后的配置（移除API密钥）

### 2. **功能请求**

对于新功能，请：
- **检查现有问题** 避免重复
- **描述用例** 和用户收益
- **考虑国际化** (中英文支持)
- **思考UI/UX** 对键盘导航的影响

### 3. **代码贡献**

#### Pull Request流程

1. **创建功能分支**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **遵循编码标准**:
   - 简洁、可读的代码，有意义的命名
   - 适当的错误处理和日志记录
   - 支持中英文双语
   - 保持键盘导航兼容性

3. **测试您的更改**:
   ```bash
   # 测试基本功能
   python -m fortune_teller
   
   # 测试i18n系统
   python -c "from fortune_teller.i18n import t; print(t('welcome_title', 'zh'))"
   
   # 测试键盘导航（交互式）
   python tests/test_keyboard.py
   ```

4. **更新文档**:
   - 如需要，更新README.md和README.zh.md
   - 在i18n/locales/中添加/更新翻译键
   - 记录新的配置选项

5. **提交pull request**:
   - 清晰的标题和描述
   - 引用相关问题
   - 包含UI更改的截图

#### 代码风格指南

- **Python**: 遵循PEP 8，使用有意义的变量名
- **Async/await**: 用于LLM调用和I/O操作
- **错误处理**: 优雅降级，用户友好的消息
- **国际化**: 所有面向用户的文本必须使用i18n系统
- **注释**: 解释复杂逻辑，特别是占卜算法

### 4. **添加新占卜系统**

要添加新的占卜系统（如易经、数字命理学）：

1. **创建MCP工具**:
   ```python
   # mcp/tools/new_system_converter.py
   #!/usr/bin/env python3
   """新占卜系统计算"""
   
   def calculate_fortune(birth_date, additional_params):
       """使用新系统计算命运"""
       # 实现代码
       return {"result": "fortune_data"}
   ```

2. **添加翻译**:
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

3. **更新UI**:
   ```python
   # 添加到 ui/keyboard_input.py select_fortune_system()
   options.append(f"🔮 {t('system_new', language)} - {t('system_new_desc', language)}")
   ```

4. **在主应用中实现**:
   ```python
   # 添加到 simple_main.py
   async def run_new_system(self):
       """运行新占卜系统"""
       # 实现代码
   ```

### 5. **国际化 (i18n)**

添加新文本时：

1. **永远不要硬编码字符串**:
   ```python
   # ❌ 错误
   print("欢迎使用霄占")
   
   # ✅ 正确
   from fortune_teller.i18n import t
   print(t("welcome_title", language))
   ```

2. **添加到两个语言文件**:
   ```json
   // en.json
   {"new_feature_title": "New Feature"}
   
   // zh.json  
   {"new_feature_title": "新功能"}
   ```

3. **使用描述性键名**:
   ```python
   # ✅ 好的键名
   t("error_invalid_date", lang)
   t("system_bazi_desc", lang)
   t("navigation_arrows", lang)
   ```

## 🧪 测试

### 手动测试

```bash
# 测试语言切换
python -m fortune_teller

# 测试流式输出
python tests/test_simple_streaming.py

# 测试i18n系统
python -m pytest tests/test_i18n_complete.py
```

### 自动化测试

```bash
# 运行所有测试
python -m pytest tests/

# 测试特定组件
python -m pytest tests/test_i18n_complete.py -v
```

## 📋 开发指南

### 提交信息

使用带表情符号的约定式提交：

```bash
# 功能
git commit -m "✨ 添加新塔罗牌阵选择"

# Bug修复  
git commit -m "🐛 修复Windows键盘导航问题"

# 文档
git commit -m "📚 更新安装说明"

# 国际化
git commit -m "🌍 添加西班牙语翻译支持"

# 重构
git commit -m "♻️ 简化LLM工具初始化"
```

### 分支命名

- `feature/add-numerology-system`
- `bugfix/keyboard-navigation-windows`
- `docs/update-contributing-guide`
- `i18n/add-spanish-support`

## 🎯 优先领域

我们特别欢迎以下方面的贡献：

1. **🌍 新语言**: 西班牙语、法语、日语翻译
2. **🔮 占卜系统**: 易经、数字命理学、符文
3. **🎨 UI改进**: 更好的动画、进度指示器
4. **🧪 测试**: 自动化测试、边缘情况处理
5. **📱 平台支持**: Windows兼容性、移动友好输出
6. **⚡ 性能**: 更快的LLM响应、缓存

## 🆘 获取帮助

- **💬 讨论**: 使用GitHub Discussions提问
- **🐛 问题**: 通过GitHub Issues报告Bug
- **📧 联系**: 联系维护者进行复杂贡献

## 📄 许可证

通过贡献，您同意您的贡献将在MIT许可证下授权。

---

**感谢您帮助霄占变得更好！** ✨
