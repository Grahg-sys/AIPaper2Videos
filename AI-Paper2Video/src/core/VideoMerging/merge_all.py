#!/usr/bin/env python3
"""
简单的视频合并工具
将多个视频文件合并为一个视频文件
"""

import os
import sys
from moviepy.editor import VideoFileClip, concatenate_videoclips


def merge_videos(video_files, output_path):
    """
    合并多个视频文件
    
    Args:
        video_files: 视频文件路径列表
        output_path: 输出文件路径
    """
    try:
        # 加载所有视频
        clips = [VideoFileClip(f) for f in video_files]
        
        # 合并视频
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # 写入输出文件
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None
        )
        
        # 清理资源
        for clip in clips:
            clip.close()
        final_clip.close()
        
        print(f"合并完成: {output_path}")
        return True
        
    except Exception as e:
        print(f"合并失败: {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python merge_all.py 输出文件 视频1 视频2 [视频3 ...]")
        print("示例: python merge_all.py merged.mp4 video1.mp4 video2.mp4")
        return
    
    output_path = sys.argv[1]
    video_files = sys.argv[2:]
    
    # 检查文件是否存在
    for f in video_files:
        if not os.path.exists(f):
            print(f"文件不存在: {f}")
            return
    
    # 合并视频
    merge_videos(video_files, output_path)


if __name__ == "__main__":
    main()
