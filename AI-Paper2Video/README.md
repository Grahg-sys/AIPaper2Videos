# AI Paper2Video

将学术论文一键转成视频的端到端流水线：PDF 解析 → 分镜脚本 → 文生图 → 图生视频 → TTS → 加字幕/配音 → 合并成片。

## 架构概览
- `main.py`：FastAPI 入口，`/run` 触发流水线、`/result/{task_id}` 查询结果。
- `src/core/Pipeline/`：核心管线 `Paper2VideoPipeline`，串起解析、分镜、生图、生成视频、TTS、字幕/配音、合并。
- `src/core/PDF_MinerU/`：调用 MinerU API 将 PDF 转 Markdown（`pdf_main.py`）。
- `src/core/PicCaptionGen/`：分镜提示词生成（`promptgen.py`）、文生图（`picgen.py`）、TTS（`tts.py`）。
- `src/core/VideoGen/`：图生视频（`videogen.py`，调用火山方舟 Ark）。
- `src/core/VideoMerging/`：字幕（`video+cap.py`）、配音（`video+voi.py`）、合并（`merge_all.py`）。
- `src/app/streamlit.py`：前端演示界面（当前为模拟流程，未与后台管线打通）。
- `config/pipeline_outputs/<task_id>/`：默认产物目录（解析的 MD、分镜 JSON、各阶段视频、音频、最终 `merged.mp4`）。

## 依赖与环境
- Python 3.9+，FFmpeg（`moviepy` 写视频需要）。
- 主要三方库见 `requirements.txt`（FastAPI、uvicorn、moviepy、volcenginesdkarkruntime、requests 等）。
- 网络调用依赖外部 API：
  - MinerU：PDF 解析。
  - 火山方舟 Ark：分镜 LLM、文生图、图生视频。
  - Baidu TTS：旁白合成（`tts.py` 默认写死 key，请自行替换）。
- 建议用虚拟环境，并提前安装 FFmpeg。

## 准备工作
1) 安装依赖
```bash
pip install -r requirements.txt
```

2) 配置密钥（至少需要替换默认硬编码的 key/token）
- `MINERU_TOKEN` 环境变量，或在构造 `Paper2VideoPipeline` 时传入 `mineru_token`。
- 火山方舟 Ark API Key：传入 `Paper2VideoPipeline(ark_api_key="...")`，或修改 `promptgen.py` / `picgen.py` / `videogen.py` 中的默认 key。
- 百度 TTS Key：更新 `src/core/PicCaptionGen/tts.py` 构造参数。

3) FFmpeg
确保 `ffmpeg` 在 PATH 中，可用 `ffmpeg -version` 检查。

## 快速开始

### 方式一：命令行跑完整管线
```bash
python src/core/Pipeline/pipeline.py
```
- 使用内置示例 PDF URL，自动生成随机 `task_id`。
- 产物输出到 `config/pipeline_outputs/<task_id>/merged.mp4`。

### 方式二：启动 FastAPI
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- 健康检查：`GET /health`
- 提交任务：`POST /run`，body `{ "pdf_url": "<PDF 下载地址>" }`
- 查结果：`GET /result/{task_id}`
- 说明：当前实现用后台任务存储在内存字典 `_TASK_RESULTS`，重启会丢失；无进度回调。

### 方式三：Streamlit 演示界面
```bash
streamlit run src/app/streamlit.py
```
- 目前 UI 仅模拟流程与进度，尚未接入真实管线/接口。

## 流水线细节（`Paper2VideoPipeline`）
1. PDF 解析：`PDFMinerUClient.extract(pdf_url)` → `paper.md`
2. 分镜生成：`PromptGenerator.generate(md)` + `paper2pic.md` 模板 → 10 帧 JSON（`storyboard.json`）
3. 文生图：`ImageGenerator.generate(visual_description_cn)` → `image_url`
4. 图生视频：`VideoGenerator.generate(text_prompt, image_url)` → `video_url`（会下载到本地）
5. TTS：`BaiduTTS.synthesize(voiceover_script_cn)` → `audio_path`
6. 加字幕：`add_subtitle` → `captioned/`
7. 加语音：`add_voice_to_video` → `voiced/`
8. 合并：`merge_videos` 按 `frame_id` 排序 → `merged.mp4`

## 目录结构（核心部分）
```
.
├── main.py
├── config/
│   └── pipeline_outputs/       # 运行后生成
├── src/
│   ├── app/streamlit.py        # 前端演示
│   ├── api/                    # 早期脚本
│   └── core/
│       ├── Pipeline/pipeline.py
│       ├── PDF_MinerU/pdf_main.py
│       ├── PicCaptionGen/{promptgen.py,picgen.py,tts.py}
│       ├── VideoGen/videogen.py
│       └── VideoMerging/{video+cap.py,video+voi.py,merge_all.py}
└── tests/
```

## 注意事项与改进建议
- **密钥安全**：当前部分 key/token 写在代码里，仅供开发测试，生产请改为环境变量或配置文件。
- **容错与重试**：外部 API 失败时无完整重试/回退逻辑，可在各阶段增加重试、超时处理。
- **资源依赖**：图生视频/文生图/TTS 依赖网络与 API 配额；`moviepy` 需要本地 FFmpeg。
- **前端对接**：Streamlit 界面尚未串联后台 FastAPI/管线，可按需对接。
- **进度与存储**：当前任务状态存内存，建议接入持久化（DB/对象存储）与进度回调。

## 开发辅助
- 单步调试：可按阶段调用 `parse_pdf` / `build_storyboard` / `generate_images` 等函数。
- 示例 PDF：`pipeline.py` 中 `example_pdf` 供调试使用。
- 输出目录清理：大量生成文件会占用空间，注意定期清理 `config/pipeline_outputs/`。
