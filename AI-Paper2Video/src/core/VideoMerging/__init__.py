"""
包装 VideoMerging 下已有脚本，方便 import 使用。
由于原始文件名包含加号（video+cap.py 等），这里用 SourceFileLoader 动态加载并导出核心函数。
"""

from importlib.machinery import SourceFileLoader
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent

_cap_mod = SourceFileLoader("video_cap", str(MODULE_DIR / "video+cap.py")).load_module()
_voi_mod = SourceFileLoader("video_voice", str(MODULE_DIR / "video+voi.py")).load_module()
_merge_mod = SourceFileLoader("merge_all", str(MODULE_DIR / "merge_all.py")).load_module()

add_subtitle = _cap_mod.add_subtitle
add_voice_to_video = _voi_mod.add_voice_to_video
merge_videos = _merge_mod.merge_videos

__all__ = ["add_subtitle", "add_voice_to_video", "merge_videos"]
