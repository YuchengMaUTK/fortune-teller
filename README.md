# 霄占 (Fortune Teller)

基于Python的多系统算命程序，使用LLM（大型语言模型）进行解读。

## 功能

- 支持多种算命系统（八字命理、塔罗牌、星座占星等）
- 插件化架构，易于扩展
- 使用LLM提供专业的解读和分析
- 命令行界面，便于使用
- 丰富的视觉呈现，包括彩色输出和表情符号
- 每种占卜系统拥有专属主题和解读领域
- 支持与占卜师聊天模式

## 项目结构

```
fortune_teller/
├── core/                       # 核心功能模块
│   ├── __init__.py
│   ├── plugin_manager.py       # 插件管理器
│   ├── base_system.py          # 基础系统接口
│   ├── llm_connector.py        # LLM连接器
│   └── config_manager.py       # 配置管理
├── plugins/                    # 各算命系统插件
│   ├── __init__.py             # 插件注册机制
│   ├── bazi/                   # 八字命理插件
│   ├── tarot/                  # 塔罗牌插件
│   └── zodiac/                 # 星座插件
├── utils/                      # 通用工具函数
│   ├── __init__.py
│   └── date_utils.py           # 日期处理工具
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

```bash
# 列出可用的占卜系统
python -m fortune_teller.main --list

# 使用特定的占卜系统
python -m fortune_teller.main --system bazi

# 保存解读结果到文件
python -m fortune_teller.main --system tarot --output reading.json
```

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

## 许可证

MIT
