"""
简单的视频加语音工具（修复版）
给无声视频添加语音，并对时长进行基础对齐
"""

import os
import sys
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np


def add_voice_to_video(video_file, audio_file, output_file):
    """
    给视频添加语音

    Args:
        video_file: 无声视频文件路径
        audio_file: 语音文件路径
        output_file: 输出文件路径
    """
    if not os.path.exists(video_file):
        raise FileNotFoundError(f"视频文件不存在: {video_file}")
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"语音文件不存在: {audio_file}")

    video = None
    audio = None
    final_video = None

    try:
        video = VideoFileClip(video_file)
        audio = AudioFileClip(audio_file)

        # 对齐时长：音频若更长则截断，若更短则用静音填充到视频长度
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        elif audio.duration < video.duration:
            # 创建静音音频片段来填充剩余时间
            silence_duration = video.duration - audio.duration
            # 获取音频的采样率和声道数
            fps = audio.fps
            nchannels = audio.nchannels
            # 创建静音数组
            silence_array = np.zeros((int(silence_duration * fps), nchannels))
            silence_clip = AudioArrayClip(silence_array, fps=fps)
            # 将原始音频和静音音频连接
            audio = concatenate_audioclips([audio, silence_clip])

        final_video = video.set_audio(audio)
        final_video.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            logger=None,
        )

        print(f"加语音完成: {output_file}")
        return True

    except Exception as e:
        print(f"加语音失败: {e}")
        return False

    finally:
        for clip in (final_video, video, audio):
            try:
                if clip:
                    clip.close()
            except Exception:
                pass


def main():
    """主函数"""
    if len(sys.argv) != 4:
        print("用法: python video+voi.py <视频文件> <语音文件> <输出文件>")
        print("示例: python video+voi.py silent.mp4 voice.mp3 output.mp4")
        return

    add_voice_to_video(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
