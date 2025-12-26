"""API端点路由"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from src.database.crud import create_task, get_task, update_task_status
from src.database.models import SessionLocal
from src.api.schemas import TaskCreate, TaskResponse, TaskStatus
from src.pipelines.cinematic_60s import Cinematic60sPipeline
from src.pipelines.student_visual import StudentVisualPipeline
from src.pipelines.academic_pres import AcademicPresentationPipeline

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=TaskResponse)
async def upload_paper(
    file: UploadFile = File(...),
    style: str = "cinematic_60s",
    db: Session = Depends(get_db)
):
    """上传论文文件并创建转换任务"""
    
    # 验证文件类型
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 创建任务记录
    task = create_task(
        db=db,
        task_id=task_id,
        filename=file.filename,
        style=style,
        status="processing"
    )
    
    # 根据风格选择处理管道
    try:
        if style == "cinematic_60s":
            pipeline = Cinematic60sPipeline(task_id, file)
        elif style == "student_visual":
            pipeline = StudentVisualPipeline(task_id, file)
        elif style == "academic_pres":
            pipeline = AcademicPresentationPipeline(task_id, file)
        else:
            raise HTTPException(status_code=400, detail="不支持的视频风格")
        
        # 异步处理任务
        await pipeline.process()
        
    except Exception as e:
        update_task_status(db, task_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    
    return TaskResponse(
        task_id=task_id,
        status="processing",
        created_at=task.created_at,
        message="任务已创建，正在处理中"
    )

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """查询任务状态"""
    
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return TaskResponse(
        task_id=task.task_id,
        status=task.status,
        video_url=task.video_url,
        thumbnail_url=task.thumbnail_url,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    
    tasks = db.query(Task).offset(skip).limit(limit).all()
    
    return [
        TaskResponse(
            task_id=task.task_id,
            status=task.status,
            video_url=task.video_url,
            thumbnail_url=task.thumbnail_url,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]

@router.delete("/task/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """删除任务"""
    
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 删除相关文件
    if task.video_url:
        # TODO: 删除存储的文件
        pass
    
    db.delete(task)
    db.commit()
    
    return {"message": "任务已删除"}