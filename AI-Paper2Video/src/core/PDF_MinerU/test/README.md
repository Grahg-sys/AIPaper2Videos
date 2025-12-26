# 梯子会导致解析结果提取失败


# MinerU PDF解析测试脚本

这个文件夹包含使用MinerU API通过URL方式解析PDF的测试脚本。

## 文件说明

- `pdf_mineru_client.py` - 主要的客户端类，支持URL方式创建解析任务
- `example_usage.py` - 使用示例，演示如何使用客户端解析PDF

## 快速开始

### 1. 运行示例

```bash
# 使用官方示例PDF
python example_usage.py
```

### 2. 使用命令行工具

```bash
# 基本用法
python pdf_mineru_client.py <pdf_url> [输出目录]

# 使用官方示例PDF
python pdf_mineru_client.py https://cdn-mineru.openxlab.org.cn/demo/example.pdf ./output
```

### 3. 使用自定义URL

修改 `example_usage.py` 中的 `custom_pdf_url` 变量，或运行脚本时按提示输入URL。

## 功能特点

- 🔗 支持URL方式解析PDF，无需上传文件
- 🔄 自动轮询解析状态
- 📥 自动下载和解压解析结果
- ⏱️ 可配置的超时和轮询间隔
- 🛡️ 完整的错误处理

## API限制

- 文件大小：不超过200MB
- 文件页数：不超过600页
- 每日额度：2000页高优先级解析
- 网络限制：GitHub、AWS等国外URL可能会超时

## 输出结果

解析结果包含：
- `markdown/` - Markdown格式的文本内容
- `images/` - 提取的图片文件
- `tables/` - 表格数据（CSV格式）
- `formulas/` - 公式（LaTeX格式）
- `metadata.json` - 文档元数据