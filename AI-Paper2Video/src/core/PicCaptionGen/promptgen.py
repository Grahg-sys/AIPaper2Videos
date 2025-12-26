"""
利用解析得到的 full.md 结合 Prompt 文件生成 10 帧分镜 JSON。
增加 JSON 强约束与重试逻辑：如果模型首次输出非 JSON，再次追加“只输出合法 JSON 数组”指令重试。
"""

import json
from pathlib import Path
from typing import Any, Optional, Tuple
import re
from datetime import datetime
from volcenginesdkarkruntime import Ark

PROMPT_FILE = Path(__file__).parent.parent / "Prompt" / "paper2pic.md"


class PromptGenerator:
    def __init__(self):
        self.client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key="81af5701-11b9-4a7c-981b-93f9437f9cc9",
        )
        self.prompt_template = PROMPT_FILE.read_text(encoding="utf-8")

    def _call_model(self, prompt: str) -> Optional[str]:
        """调用 Ark，返回原始文本。"""
        result = self.client.responses.create(
            model="doubao-seed-1-6-flash-250828",
            input=prompt,
        )
        
        result=result.output[1].content[0].text
    
        return result
    def generate(self, document_md: str, extra_instruction: Optional[str] = None) -> Optional[str]:
        """接受文档 md，返回模型回复的文本内容，可附加额外指令。"""
        full_prompt = f"{self.prompt_template}\n\n{document_md}"
        if extra_instruction:
            full_prompt = f"{full_prompt}\n\n{extra_instruction}"
        return self._call_model(full_prompt)


if __name__ == "__main__":
    # 使用示例
    # 方式1: 直接使用md内容
    generator = PromptGenerator()
    sample_md = """
    量子力学是研究微观粒子（如原子、电子、光子）运动规律的物理学分支，它颠覆了经典力学的确定性框架，揭示微观世界具有波粒二象性、不确定性原理、量子叠加与纠缠等独特特性。其理论不仅推动了半导体、激光、量子计算等技术的诞生，也重塑了人类对物质本质的认知。
    """
    result = generator.generate(sample_md)
    print(result)
    
