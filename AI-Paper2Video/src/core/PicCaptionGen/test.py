# 利用解析得到的full.md,结合Prompt文件夹里的paper2pic，生成生图提示词和对应的字幕

from pathlib import Path
from volcenginesdkarkruntime import Ark




class PromptGenerator:
    def __init__(self):
        self.client = Ark(
            base_url='https://ark.cn-beijing.volces.com/api/v3',
            api_key='81af5701-11b9-4a7c-981b-93f9437f9cc9',
        )
    def generate(self):
        """接受文档md，返回模型结果"""
        full_prompt = "你好"
        return self.client.responses.create(
            model="doubao-seed-1-6-251015",
            input=full_prompt
        )


if __name__ == "__main__":
    # 使用示例
    # 方式1: 直接使用md内容
    generator = PromptGenerator()
    result = generator.generate()
    print("生成结果:", result)
    
