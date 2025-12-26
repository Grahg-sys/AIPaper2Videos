# AI Paper2Video 项目

将学术论文智能转化为高质量视频内容的AI系统。

## 功能特性

- 📄 PDF论文智能解析
- 🎯 可科普性评估
- 📝 智能分镜脚本生成
- 🎨 AI图像生成
- 🎬 视频合成与特效
- 🔊 TTS配音生成
- 📊 多种输出格式（60s短视频/学术汇报）

## 项目结构

```
AI-Paper2Video/
├── config/          # 配置文件
├── src/            # 源代码
│   ├── api/        # API接口
│   ├── core/       # 核心算法
│   ├── pipelines/  # 业务流程
│   ├── database/   # 数据存储
│   └── utils/      # 工具类
├── tests/          # 测试用例
└── static/         # 静态文件
```

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入API密钥
```

3. 运行项目
```bash
python main.py
```

## API文档

启动服务后访问: http://localhost:8000/docs

## 许可证

MIT License