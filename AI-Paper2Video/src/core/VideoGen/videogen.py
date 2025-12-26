import time
import base64
from pathlib import Path
from volcenginesdkarkruntime import Ark


class VideoGenerator:
    """视频生成器类"""
    
    def __init__(self, base_url="https://ark.cn-beijing.volces.com/api/v3", 
                 api_key='81af5701-11b9-4a7c-981b-93f9437f9cc9',
                 model="doubao-seedance-1-5-pro-251215"):
        self.client = Ark(base_url=base_url, api_key=api_key)
        self.model = model
    
    def _get_image_data(self, image_path_or_url):
        """处理图片：URL直接返回，本地文件转为base64"""
        if image_path_or_url.startswith(('http://', 'https://')):
            return {"url": image_path_or_url}
        
        path = Path(image_path_or_url)
        if not path.exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path_or_url}")
        
        mime_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', 
                    '.gif': 'image/gif', '.webp': 'image/webp'}
        mime = mime_map.get(path.suffix.lower(), 'image/jpeg')
        
        with open(path, 'rb') as f:
            return {"url": f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"}
    
    def _wait_for_task(self, task_id):
        """等待任务完成"""
        while True:
            task = self.client.content_generation.tasks.get(task_id=task_id)
            if task.status == "succeeded":
                return task
            if task.status == "failed":
                raise Exception(f"任务失败: {task.error}")
            time.sleep(1)
    
    def generate(self, text, image):
        """
        生成视频
        
        Args:
            text: 视频描述文本（可包含参数，如 "--wm true --dur 5"）
            image: 图片路径或URL
        
        Returns:
            视频URL字符串，如果任务失败或没有video_url则返回None
        """
        result = self.client.content_generation.tasks.create(
            model=self.model,
            content=[
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": self._get_image_data(image)}
            ]
        )
        print(f"任务已创建: {result.id}")
        task = self._wait_for_task(result.id)
        print("任务成功完成")
        
        # 提取 video_url
        video_url = None
        if hasattr(task, 'content') and task.content:
            video_url = getattr(task.content, 'video_url', None)
        
        return video_url


if __name__ == "__main__":
    # 示例1: 使用本地图片
    generator = VideoGenerator()
    video_url = generator.generate(
        text="小猪左右跑动 --wm true --dur 5",
        image=r"C:\Users\23154\Desktop\AI硬件项目\AI文献视觉\AI-Paper2Video\config\i2v_foxrgirl.png"
    )
    print(f"视频URL: {video_url}")
    
    # 示例2: 使用网络图片URL
    # generator = VideoGenerator()
    # video_url = generator.generate(
    #     text="一只狐狸在跳舞 --wm true --dur 3",
    #     image="https://ark-project.tos-cn-beijing.volces.com/doc_image/i2v_foxrgirl.png"
    # )
    # print(f"视频URL: {video_url}")
