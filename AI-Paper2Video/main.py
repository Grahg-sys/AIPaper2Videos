"""
FastAPI 入口，提供一个简易接口触发 Paper2VideoPipeline。
运行:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import uuid
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

# 确保项目根可被导入
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.Pipeline.pipeline import Paper2VideoPipeline  # noqa: E402

app = FastAPI(
    title="AI Paper2Video",
    description="调用 pipeline 将论文转换为视频的简单接口",
    version="0.1.0",
)


class RunRequest(BaseModel):
    pdf_url: str
    task_id: Optional[str] = None


class RunResponse(BaseModel):
    task_id: str
    status: str
    message: str
    merged_video: Optional[str] = None


def _run_pipeline_task(task_id: str, pdf_url: str):
    pipeline = Paper2VideoPipeline(task_id=task_id)
    artifacts = pipeline.run(pdf_url)
    return artifacts


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run_pipeline(body: RunRequest, background: BackgroundTasks):
    if not body.pdf_url:
        raise HTTPException(status_code=400, detail="pdf_url 不能为空")

    task_id = body.task_id or f"api-{uuid.uuid4().hex[:8]}"

    # 简单实现：直接后台执行，返回立即响应
    def runner():
        try:
            artifacts = _run_pipeline_task(task_id, body.pdf_url)
            _TASK_RESULTS[task_id] = {
                "status": "completed",
                "merged": str(artifacts.merged_video_path) if artifacts.merged_video_path else None,
            }
        except Exception as e:
            _TASK_RESULTS[task_id] = {"status": "failed", "error": str(e)}

    background.add_task(runner)

    return RunResponse(
        task_id=task_id,
        status="processing",
        message="任务已提交，稍后查询 /result/{task_id}",
    )


_TASK_RESULTS = {}


@app.get("/result/{task_id}", response_model=RunResponse)
async def get_result(task_id: str):
    result = _TASK_RESULTS.get(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="任务不存在或尚未开始")
    return RunResponse(
        task_id=task_id,
        status=result.get("status", "unknown"),
        message=result.get("error", "ok"),
        merged_video=result.get("merged"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
