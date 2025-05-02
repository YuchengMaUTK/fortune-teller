# 贡献指南

感谢您对霄占 (Fortune Teller) 项目的兴趣！我们欢迎并鼓励社区贡献。

## 如何贡献

有多种方式可以为项目做出贡献：

1. **报告Bug**：使用GitHub的Issues功能提交bug报告
2. **提交功能建议**：同样使用Issues提交新功能建议
3. **提交代码**：通过Pull Request贡献代码
4. **改进文档**：帮助我们改进文档

## 贡献流程

1. Fork项目仓库
2. 创建自己的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 代码风格

- 使用4个空格缩进（不使用制表符）
- 遵循PEP 8风格指南
- 提供详细的注释，特别是对于复杂的逻辑
- 为新功能编写测试

## 贡献新的占卜系统

如果您想贡献新的占卜系统，请遵循以下步骤：

1. 在`fortune_teller/plugins/`下创建新目录
2. 实现继承自`BaseFortuneSystem`的系统类
3. 创建`manifest.yaml`描述插件
4. 在`__init__.py`中注册插件
5. 如果需要，在`data/`目录下添加相关数据文件
6. 编写详细的文档说明如何使用新系统

## Pull Request准则

- 更新README.md说明新增功能的用法（如适用）
- 如果增加新依赖，更新requirements.txt
- Pull Request应该指向`main`分支
- 确保代码能在各大主流操作系统上运行

## 联系

如有任何疑问，请通过GitHub Issues联系我们。

感谢您的贡献！
