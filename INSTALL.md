# 安装指南

本文档提供了安装和设置霄占命理解析系统的详细步骤。

## 系统需求

- Python 3.9 或更高版本
- pip (Python包管理器)
- 互联网连接（用于安装依赖和连接LLM API）

## 基本安装

1. **克隆仓库**

```bash
git clone https://github.com/your-username/fortune-teller.git
cd fortune-teller
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **开发模式安装**

如果您打算对代码进行修改或贡献，建议以开发模式安装：

```bash
pip install -e .
```

## 配置设置

### 配置文件设置

1. **创建配置文件**

```bash
# 从示例文件复制
cp config.yaml.example config.yaml
```

2. **编辑配置文件**

根据您选择的LLM提供商编辑`config.yaml`文件：

```yaml
llm:
  provider: "aws_bedrock"  # 可选: "openai", "anthropic", "aws_bedrock", "mock"
  model: "anthropic.claude-3-sonnet-20240229-v1:0"  # 根据提供商选择适当的模型
```

### 环境变量设置

根据您选择的LLM提供商，设置相应的环境变量：

#### OpenAI

```bash
export OPENAI_API_KEY="your_api_key_here"
```

#### Anthropic直连

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

#### AWS Bedrock

```bash
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_REGION="us-east-1"  # 或其他适用地区
```

## 测试安装

### 测试模式（无需API密钥）

如果您只想测试功能而不连接真实的LLM服务：

```bash
# 使用模拟配置
cp config.yaml.mock config.yaml

# 运行程序
python -m fortune_teller.main
```

### 验证正常安装

```bash
# 查看可用命令
python -m fortune_teller.main --help

# 列出支持的占卜系统
python -m fortune_teller.main --list
```

## 疑难解答

如果遇到LLM连接问题，可以使用提供的工具脚本进行测试：

```bash
# 测试AWS Bedrock连接
python test_aws_bedrock.py

# 排查LLM连接问题
python troubleshoot_llm.py
```

## 目录结构

安装完成后，您的项目结构应该如下所示：

```
fortune_teller/
├── core/              # 核心功能
├── data/              # 占卜系统数据文件
├── plugins/           # 占卜系统插件
├── ui/                # 用户界面
├── utils/             # 通用工具
└── __init__.py        # 包初始化文件
```

## 下一步

安装完成后，请参阅README.md了解使用方法，或查阅CONTRIBUTING.md了解如何为项目贡献代码。
