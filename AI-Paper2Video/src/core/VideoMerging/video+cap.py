"""简单的视频加字幕工具（修复版，无需 ImageMagick）"""

import os
import numpy as np
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont, ImageColor


def add_subtitle(
    video_file,
    subtitle_text,
    output_file,
    fontsize=40,
    font="Arial",
    color="white",
    stroke_color="black",
    stroke_width=3,
    bg_color="rgba(0,0,0,160)",
    padding=16,
):
    """
    给视频添加字幕并导出

    Args:
        video_file: 输入视频路径
        subtitle_text: 字幕文本
        output_file: 输出视频路径
        fontsize: 字体大小
        font: 字体名称（需要本地安装）
        color: 字体颜色
        stroke_color: 描边颜色
        stroke_width: 描边宽度
        bg_color: 背景色（支持 rgba），让文字更清晰
        padding: 背景内边距像素
    """
    if not os.path.exists(video_file):
        raise FileNotFoundError(f"视频不存在: {video_file}")

    clip = None
    txt_clip = None
    video = None
    try:
        clip = VideoFileClip(video_file)

        # 优先尝试 TextClip（需要 ImageMagick）；失败则走 PIL 渲染
        try:
            txt_clip = TextClip(
                subtitle_text,
                fontsize=fontsize,
                color=color,
                font=font,
                method="caption",
                size=(int(clip.w * 0.95), None),
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                align="center",
            ).set_duration(clip.duration).set_position(("center", "bottom"))
        except Exception:
            txt_clip = _pil_text_clip(
                subtitle_text,
                video_width=clip.w,
                fontsize=fontsize,
                font=font,
                color=color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                duration=clip.duration,
                bg_color=bg_color,
                padding=padding,
            )

        video = CompositeVideoClip([clip, txt_clip])
        video.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            logger=None,
        )
        print(f"完成: {output_file}")
    finally:
        for c in (video, txt_clip, clip):
            try:
                if c:
                    c.close()
            except Exception:
                pass


def _pil_text_clip(
    subtitle_text,
    video_width,
    fontsize,
    font,
    color,
    stroke_color,
    stroke_width,
    duration,
    bg_color="rgba(0,0,0,160)",
    padding=24,
):
    """用 Pillow 渲染文字，避免 ImageMagick 依赖"""
    max_width = int(video_width * 0.98)

    # 颜色解析（容错：回退白/黑）
    try:
        fill_color = ImageColor.getrgb(color)
    except Exception:
        fill_color = (255, 255, 255)
    try:
        stroke_fill = ImageColor.getrgb(stroke_color)
    except Exception:
        stroke_fill = (0, 0, 0)
    try:
        bg_rgba = ImageColor.getcolor(bg_color, "RGBA")
    except Exception:
        bg_rgba = (0, 0, 0, 160)

    # 选择字体，优先用户传入路径/名称，其次常见系统字体，再退回 Pillow 自带字体
    font_candidates = []
    if font:
        font_candidates.append(font)
    font_candidates.extend([
        r"C:\Windows\Fonts\msyh.ttc",  # 微软雅黑（中文较好）
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\arial.ttf",
        "DejaVuSans-Bold.ttf",
    ])

    font_obj = None
    for fc in font_candidates:
        try:
            font_obj = ImageFont.truetype(fc, fontsize)
            break
        except Exception:
            continue
    if font_obj is None:
        font_obj = ImageFont.load_default()

    # 按宽度拆行
    lines = []
    for raw_line in subtitle_text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        current = ""
        for word in line.split(" "):
            candidate = (current + " " + word).strip()
            if font_obj.getlength(candidate) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

    if not lines:
        lines = [subtitle_text]

    ascent, descent = font_obj.getmetrics()
    line_height = ascent + descent + stroke_width
    text_height = line_height * len(lines)
    img_height = text_height + padding * 2
    img_width = max_width + padding * 2

    img = Image.new("RGBA", (img_width, img_height), bg_rgba)
    draw = ImageDraw.Draw(img)

    y = padding
    for line in lines:
        text_width = font_obj.getlength(line)
        x = max((img_width - text_width) / 2, padding)
        draw.text(
            (x, y),
            line,
            font=font_obj,
            fill=fill_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        y += line_height

    return (
        ImageClip(np.array(img))
        .set_duration(duration)
        .set_position(("center", "bottom"))
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("用法: python video+cap.py <视频文件> <字幕文本> <输出文件> [字体大小]")
        print("示例: python video+cap.py input.mp4 \"Hello World\" output.mp4 192")
        sys.exit(1)

    add_subtitle(
        video_file=sys.argv[1],
        subtitle_text=sys.argv[2],
        output_file=sys.argv[3],
        fontsize=40,
    )

