"""Pydantic数据模型"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoStyle(str, Enum):
    CINEMATIC_60S = "cinematic_60s"
    STUDENT_VISUAL = "student_visual"
    ACADEMIC_PRES = "academic_pres"

class TaskCreate(BaseModel):
    """创建任务请求模型"""
    filename: str = Field(..., description="论文文件名")
    style: VideoStyle = Field(default=VideoStyle.CINEMATIC_60S, description="视频风格")
    custom_prompt: Optional[str] = Field(None, description="自定义提示词")
    
class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    video_url: Optional[str] = Field(None, description="视频文件URL")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    message: Optional[str] = Field(None, description="状态描述")

class PaperAnalysis(BaseModel):
    """论文分析结果"""
    title: str = Field(..., description="论文标题")
    authors: List[str] = Field(default_factory=list, description="作者列表")
    abstract: str = Field(..., description="摘要")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    difficulty_score: float = Field(..., description="可科普性评分 (1-10)")
    key_concepts: List[str] = Field(default_factory=list, description="核心概念")
    visual_elements: List[str] = Field(default_factory=list, description="可视化元素")

class ScriptSegment(BaseModel):
    """分镜脚本片段"""
    segment_id: int = Field(..., description="片段ID")
    timestamp: str = Field(..., description="时间戳")
    duration: float = Field(..., description="持续时间")
    narration: str = Field(..., description="旁白文案")
    visual_description: str = Field(..., description="视觉描述")
    transition: Optional[str] = Field(None, description="转场效果")

class VideoScript(BaseModel):
    """视频脚本"""
    title: str = Field(..., description="视频标题")
    total_duration: float = Field(..., description="总时长")
    style: VideoStyle = Field(..., description="视频风格")
    segments: List[ScriptSegment] = Field(default_factory=list, description="分镜片段")
    
class GeneratedAsset(BaseModel):
    """生成的资源"""
    asset_id: str = Field(..., description="资源ID")
    asset_type: str = Field(..., description="资源类型 (image/audio/video)")
    file_url: str = Field(..., description="文件URL")
    metadata: Optional[dict] = Field(default_factory=dict, description="元数据")