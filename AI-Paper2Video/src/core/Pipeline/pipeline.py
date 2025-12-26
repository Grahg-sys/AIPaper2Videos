"""
End-to-end pipeline for PDF -> storyboard -> images -> videos -> TTS/merge.
依赖外部 API：MinerU（PDF 解析）、Doubao（文生图、图生视频）、edge-tts（本地语音）。
视频加字幕/加语音/合并调用现有脚本（video+cap.py、video+voi.py、merge_all.py）。
"""

import json
import os
import shutil
from dataclasses import dataclass, field
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from time import perf_counter
import uuid
import sys

import requests

# 保证可以从任意工作目录运行
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.PDF_MinerU.pdf_main import PDFMinerUClient
from src.core.VideoGen.videogen import VideoGenerator
from src.core.VideoMerging import add_subtitle, add_voice_to_video, merge_videos
from src.core.PicCaptionGen.tts import BaiduTTS

DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "config" / "pipeline_outputs"
VIDEO_MERGING_DIR = PROJECT_ROOT / "src" / "core" / "VideoMerging"
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"


@dataclass
class FrameArtifact:
    frame_id: int
    title_cn: str
    voiceover_script_cn: str
    visual_description_cn: str
    image_url: Optional[str] = None
    motion_prompt_en: Optional[str] = None
    video_url: Optional[str] = None
    local_video_path: Optional[Path] = None
    audio_path: Optional[Path] = None
    captioned_video_path: Optional[Path] = None
    voiced_video_path: Optional[Path] = None


@dataclass
class PipelineArtifacts:
    task_id: str
    md_path: Optional[Path] = None
    storyboard_path: Optional[Path] = None
    frames: List[FrameArtifact] = field(default_factory=list)
    merged_video_path: Optional[Path] = None


class Paper2VideoPipeline:
    """
    论文→分镜→图片→视频→语音→合成 的同步管线
    仅组织调用，具体模型能力由各子模块提供。
    """

    def _log(self, message: str) -> None:
        print(f"[pipeline][{self.task_id}] {message}")

    def _time_it(self, label: str, fn, *args, **kwargs):
        start = perf_counter()
        result = fn(*args, **kwargs)
        elapsed = perf_counter() - start
        self._log(f"{label} 用时 {elapsed:.2f}s")
        return result

    def __init__(
        self,
        task_id: str,
        output_root: Path = DEFAULT_OUTPUT_ROOT,
        mineru_token: Optional[str] = None,
        ark_api_key: Optional[str] = None,
        tts_voice: str = DEFAULT_VOICE,
    ):
        self.task_id = task_id
        self.output_root = output_root
        self.tts_voice = tts_voice
        # 优先使用传入 token，否则使用 PDFMinerUClient 默认 token
        self.pdf_client = PDFMinerUClient(token=mineru_token) if mineru_token else PDFMinerUClient()
        self.prompt_gen = self._load_prompt_generator()
        self.image_gen = self._load_image_generator()
        self.tts_client = BaiduTTS()
        self.video_gen = VideoGenerator(api_key=ark_api_key) if ark_api_key else VideoGenerator()
        self._ensure_dirs()

    # ---------- 路径与文件 ----------
    def _ensure_dirs(self) -> None:
        for path in self._paths().values():
            if path.suffix:
                path.parent.mkdir(parents=True, exist_ok=True)
            else:
                path.mkdir(parents=True, exist_ok=True)

    def _paths(self) -> Dict[str, Path]:
        base = self.output_root / self.task_id
        return {
            "base": base,
            "md": base / "paper.md",
            "storyboard": base / "storyboard.json",
            "audio": base / "audio",
            "videos": base / "videos",
            "captioned": base / "captioned",
            "voiced": base / "voiced",
            "merged": base / "merged.mp4",
        }

    # ---------- PDF 解析 ----------

    def _load_prompt_generator(self):
        """动态加载避免硬编码包名。"""
        root = Path(__file__).resolve().parent.parent / "PicCaptionGen"
        mod = SourceFileLoader("promptgen_mod", str(root / "promptgen.py")).load_module()
        return mod.PromptGenerator()

    def _load_image_generator(self):
        root = Path(__file__).resolve().parent.parent / "PicCaptionGen"
        mod = SourceFileLoader("picgen_mod", str(root / "picgen.py")).load_module()
        return mod.ImageGenerator()

    def parse_pdf(self, pdf_url: str) -> Tuple[Path, str]:
        self._log(f"开始解析 PDF: {pdf_url}")
        md_content = self.pdf_client.extract(pdf_url=pdf_url, output_dir=str(self._paths()["base"]))
        self._paths()["md"].write_text(md_content, encoding="utf-8")
        self._log("PDF 解析完成，已写入 paper.md")
        return self._paths()["md"], md_content

    # ---------- 分镜生成 ----------
    def build_storyboard(self, md_content: str) -> Tuple[Path, List[FrameArtifact]]:
        self._log("开始生成分镜脚本")
        raw = self.prompt_gen.generate(md_content)
        raw_path = self._paths()["base"] / "storyboard_raw.txt"
        if raw:
            raw_path.write_text(str(raw), encoding="utf-8")
            self._log(f"模型原始输出已写入 {raw_path}")
            self._log(f"模型原始输出预览: {str(raw)[:200]}")
        if raw is None:
            raise RuntimeError("模型无返回")
        try:
            data = json.loads(raw)
        except Exception:
            self._log("分镜解析失败，追加强约束重试一次")
            extra = (
                "上一次输出不是合法 JSON。请严格输出 JSON 数组，仅包含字段 "
                "frame_id/title_cn/voiceover_script_cn/visual_description_cn/img2vid_motion_prompt_en，"
                "不要任何解释或多余文本。"
            )
            raw = self.prompt_gen.generate(md_content, extra_instruction=extra)
            if raw:
                raw_path.write_text(str(raw), encoding="utf-8")
                self._log(f"模型原始输出已写入 {raw_path}")
                self._log(f"模型原始输出预览: {str(raw)[:200]}")
            data = json.loads(raw)

        frames: List[FrameArtifact] = []
        for item in data:
            frames.append(
                FrameArtifact(
                    frame_id=item.get("frame_id"),
                    title_cn=item.get("title_cn", ""),
                    voiceover_script_cn=item.get("voiceover_script_cn", ""),
                    visual_description_cn=item.get("visual_description_cn", ""),
                    motion_prompt_en=item.get("img2vid_motion_prompt_en", ""),
                )
            )

        self._paths()["storyboard"].write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self._log("分镜生成完成，已写入 storyboard.json")
        return self._paths()["storyboard"], frames

    # ---------- 文生图 ----------
    def generate_images(self, frames: List[FrameArtifact]) -> None:
        self._log("开始文生图，共 {} 帧".format(len(frames)))
        for frame in frames:
            frame.image_url = self.image_gen.generate(frame.visual_description_cn)
            self._log(f"帧 {frame.frame_id} 文生图完成: {frame.image_url}")

    # ---------- 图生视频 ----------
    def generate_videos(self, frames: List[FrameArtifact]) -> None:
        self._log("开始图生视频")
        for frame in frames:
            # 优先使用分镜里的动效提示词，缺失则回落到旁白
            text_prompt = frame.motion_prompt_en 
            frame.video_url = self.video_gen.generate(text=text_prompt, image=frame.image_url)
            self._log(f"帧 {frame.frame_id} 图生视频完成: {frame.video_url}")

    def _download_if_needed(self, url_or_path: str, dest_dir: Path) -> Path:
        dest_dir.mkdir(parents=True, exist_ok=True)
        if url_or_path.startswith(("http://", "https://")):
            filename = url_or_path.split("/")[-1].split("?")[0] or "video.mp4"
            target = dest_dir / filename
            with requests.get(url_or_path, stream=True) as r:
                r.raise_for_status()
                with open(target, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            self._log(f"下载视频到本地: {target}")
            return target
        return Path(url_or_path)

    def prepare_local_videos(self, frames: List[FrameArtifact]) -> None:
        self._log("准备本地视频文件")
        for frame in frames:
            if not frame.video_url:
                continue
            frame.local_video_path = self._download_if_needed(frame.video_url, self._paths()["videos"])

    # ---------- TTS ----------
    def synthesize_audios(self, frames: List[FrameArtifact]) -> None:
        self._log("开始 TTS 生成语音")
        audio_dir = self._paths()["audio"]
        for frame in frames:
            if not frame.voiceover_script_cn:
                continue
            output_path = audio_dir / f"frame_{frame.frame_id}.mp3"
            try:
                audio_url = self.tts_client.synthesize(frame.voiceover_script_cn)
                with requests.get(audio_url, stream=True) as r:
                    r.raise_for_status()
                    with open(output_path, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
                frame.audio_path = output_path
                self._log(f"帧 {frame.frame_id} 语音生成完成: {output_path}")
            except Exception as exc:
                self._log(f"帧 {frame.frame_id} 语音生成失败: {exc}")

    # ---------- 加字幕 ----------
    def add_captions(self, frames: List[FrameArtifact], fontsize: int = 40) -> None:
        self._log("开始为视频加字幕")
        caption_dir = self._paths()["captioned"]
        for frame in frames:
            if not frame.local_video_path:
                continue
            output = caption_dir / f"frame_{frame.frame_id}_cap.mp4"
            add_subtitle(
                video_file=str(frame.local_video_path),
                subtitle_text=frame.voiceover_script_cn,
                output_file=str(output),
                fontsize=fontsize,
            )
            frame.captioned_video_path = output
            self._log(f"帧 {frame.frame_id} 加字幕完成: {output}")

    # ---------- 加语音 ----------
    def add_voices(self, frames: List[FrameArtifact]) -> None:
        self._log("开始为视频加语音")
        voiced_dir = self._paths()["voiced"]
        for frame in frames:
            # 递进：必须使用已加字幕的视频，否则跳过
            target_video = frame.captioned_video_path
            if not target_video:
                self._log(f"帧 {frame.frame_id} 缺少字幕视频，跳过加语音")
                continue
            if not frame.audio_path:
                self._log(f"帧 {frame.frame_id} 缺少音频，跳过加语音")
                continue
            output = voiced_dir / f"frame_{frame.frame_id}_voiced.mp4"
            add_voice_to_video(
                video_file=str(target_video),
                audio_file=str(frame.audio_path),
                output_file=str(output),
            )
            frame.voiced_video_path = output
            self._log(f"帧 {frame.frame_id} 加语音完成: {output}")

    # ---------- 合并 ----------
    def merge_videos(self, frames: List[FrameArtifact]) -> Optional[Path]:
        ordered = sorted(
            [f for f in frames if f.voiced_video_path],
            key=lambda x: x.frame_id,
        )
        if not ordered:
            return None
        output = self._paths()["merged"]
        merge_videos([str(f.voiced_video_path) for f in ordered], str(output))
        self._log(f"合并完成: {output}")
        return output

    # ---------- 全流程 ----------
    def run(self, pdf_url: str) -> PipelineArtifacts:
        self._log("启动 Pipeline")
        start_total = perf_counter()
        artifacts = PipelineArtifacts(task_id=self.task_id)
        artifacts.md_path, md_content = self._time_it("PDF 解析", self.parse_pdf, pdf_url)
        artifacts.storyboard_path, artifacts.frames = self._time_it("分镜生成", self.build_storyboard, md_content)
        self._time_it("文生图生成", self.generate_images, artifacts.frames)
        self._time_it("图生视频生成", self.generate_videos, artifacts.frames)
        self._time_it("下载/准备视频", self.prepare_local_videos, artifacts.frames)
        self._time_it("TTS 生成语音", self.synthesize_audios, artifacts.frames)
        self._time_it("加字幕", self.add_captions, artifacts.frames)
        self._time_it("加语音", self.add_voices, artifacts.frames)
        artifacts.merged_video_path = self._time_it("合并视频", self.merge_videos, artifacts.frames)
        total_elapsed = perf_counter() - start_total
        self._log(f"Pipeline 全部完成，用时 {total_elapsed:.2f}s")
        return artifacts


if __name__ == "__main__":
    """
    简单可运行示例：
    python src/core/Pipeline/pipeline.py
    使用 pdf_main.py 中的示例 PDF URL 跑完整流程，产物位于 config/pipeline_outputs/<task_id>/。
    """
    #example_pdf = "https://cdn-mineru.openxlab.org.cn/demo/example.pdf"
    example_pdf = "https://arxiv.org/pdf/2408.03175"
    task_id = f"demo-{uuid.uuid4().hex[:8]}"
    pipeline = Paper2VideoPipeline(task_id=task_id)
    result = pipeline.run(example_pdf)
    print(
        "Pipeline 完成",
        f"task_id={task_id}",
        f"merged={result.merged_video_path}",
        sep="\n",
    )
