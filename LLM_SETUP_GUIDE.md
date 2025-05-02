# LLM 设置指南

本文档将指导您如何为 Fortune Teller 应用程序设置大型语言模型 (LLM) 连接。

## 1. API 密钥配置

首先，您需要设置相应的 API 密钥作为环境变量：

### 对于 OpenAI 模型 (GPT-3.5, GPT-4 等)

```bash
# Linux/macOS
export OPENAI_API_KEY="your_openai_api_key_here"

# Windows (Command Prompt)
set OPENAI_API_KEY=your_openai_api_key_here

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your_openai_api_key_here"
```

### 对于 Anthropic 模型 (Claude 等)

```bash
# Linux/macOS
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "your_anthropic_api_key_here"
```

## 2. 通过配置文件设置

您也可以创建一个配置文件来设置 LLM 参数。在项目根目录创建 `config.yaml` 文件：

```yaml
llm:
  provider: "openai"  # 可选值: "openai", "anthropic"
  model: "gpt-4"      # OpenAI: "gpt-3.5-turbo", "gpt-4" 等; Anthropic: "claude-2", "claude-instant-1" 等
  temperature: 0.7    # 创造性程度 (0.0-1.0)
  max_tokens: 2000    # 返回的最大标记数
  api_key: "your_api_key_here"  # 可选，推荐使用环境变量
```

## 3. 程序内 LLM 设置

运行程序时，您可以直接修改 LLM 设置：

```python
from fortune_teller import FortuneTeller

# 初始化 Fortune Teller
fortune_teller = FortuneTeller()

# 修改 LLM 设置
fortune_teller.llm_connector.set_provider("anthropic")
fortune_teller.llm_connector.set_model("claude-2")
fortune_teller.llm_connector.temperature = 0.5
fortune_teller.llm_connector.max_tokens = 1500
```

## 4. 安装必要的依赖

确保已安装 LLM 提供商的 API 客户端库：

```bash
# 对于 OpenAI
pip install openai>=1.0.0

# 对于 Anthropic
pip install anthropic>=0.3.0
```

## 5. 选择合适的模型

### OpenAI 模型建议

- **gpt-3.5-turbo**: 较快速和经济的选择，适合大多数基本解读
- **gpt-4**: 质量更高的解读，特别是对复杂的八字和占星分析

### Anthropic 模型建议

- **claude-instant-1**: 速度更快的选择
- **claude-2**: 更全面和深入的分析能力

## 6. 排障指南

如果遇到 LLM 连接问题：

1. 确认 API 密钥设置正确且未过期
2. 检查网络连接是否正常
3. 确认选择的模型名称拼写正确
4. 检查 API 调用限制是否已达到
5. 查看 `fortune_teller.log` 文件中的详细错误信息

## 7. 使用模拟模式进行测试

如果您想在没有实际 API 密钥的情况下测试应用程序，可以设置一个不支持的提供商，系统将使用模拟模式：

```yaml
llm:
  provider: "mock"
  model: "mock-model"
```

这将返回简单的模拟响应，便于测试应用程序的其他部分功能。
