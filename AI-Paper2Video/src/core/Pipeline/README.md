# Pipeline 说明

该模块实现论文转视频的端到端流水线，核心类 `Paper2VideoPipeline` 位于 `pipeline.py`。

## 流程概览
- PDF 解析：调用 `PDFMinerUClient.extract` 将 PDF 转为 Markdown。
- 分镜生成：用 `PromptGenerator` + `paper2pic.md` 产出 10 帧 JSON 分镜。
- 文生图：`ImageGenerator` 根据每帧的中文视觉描述生成图片 URL。
- 图生视频：`VideoGenerator` 基于图片和文案生成短视频。
- TTS：使用 edge-tts 为每帧生成旁白音频。
- 加字幕 / 加语音：动态加载 `video+cap.py`、`video+voi.py` 给视频加字幕和语音。
- 合并：动态加载 `merge_all.py` 按 frame_id 顺序拼接为最终视频。

## 产物路径
默认输出目录：`config/pipeline_outputs/<task_id>/`，包含：
- `paper.md`：PDF 解析后的 Markdown。
- `storyboard.json`：10 帧分镜 JSON。
- `audio/`：每帧语音 wav。
- `videos/`：下载的帧视频（如为 URL 会下载）。
- `captioned/`：加字幕的视频。
- `voiced/`：加语音的视频。
- `merged.mp4`：最终合并结果。

## 快速运行示例
在项目根目录执行：
```bash
python src/core/Pipeline/pipeline.py
```
使用示例 PDF URL 跑完整流程，生成随机 `task_id` 并输出最终视频路径。

## 配置
- MinerU Token：环境变量 `MINERU_TOKEN`（推荐）或构造 `Paper2VideoPipeline(task_id, mineru_token="...")` 传入。
- Doubao Ark API Key：`ark_api_key="..."` 传入 `Paper2VideoPipeline`。
- TTS 声音：参数 `tts_voice`（默认 `zh-CN-XiaoxiaoNeural`）。

## 后续可扩展
- 接入分镜动效提示词生成（`motion_prompt_en`）。
- 异步化/并行化各阶段，增加重试和缓存。
- 将输出写入数据库/对象存储，并在 API 路由中返回进度。
