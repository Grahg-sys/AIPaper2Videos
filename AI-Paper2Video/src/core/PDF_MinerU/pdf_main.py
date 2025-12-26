import os
import time
import zipfile
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 默认使用内置 token；若需替换，可在实例化时传入 token 或设置环境变量 MINERU_TOKEN
DEFAULT_TOKEN = os.getenv("MINERU_TOKEN") or "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiIzMzEwNjY5MSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2NTg4OTE1NCwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiIiwib3BlbklkIjpudWxsLCJ1dWlkIjoiMTE3MzczNGEtNDUzNy00ZDZhLWI4OGItNThhYmFmNmExZmI2IiwiZW1haWwiOiIiLCJleHAiOjE3NjcwOTg3NTR9.eu6mbKibIIJEPNP14JOPKFMFZnrjQfE1YtRyanZaJ0M3xH6oS28L8S0Na8C839BN9H_WyFDAtjbIVhxFAyUBCQ"


class PDFMinerUClient:
    def __init__(self, token: str = DEFAULT_TOKEN, base_url: str = "https://mineru.net/api/v4"):
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        self.base_url = base_url
    
    def _check(self, res):
        data = res.json()
        if data.get("code") != 0:
            raise Exception(data.get('msg', '未知错误'))
        return data["data"]
    
    def extract(self, pdf_url: str, model_version: str = "vlm", output_dir: str = "./output", max_wait: int = 600):
        task_id = self._check(self.session.post(f"{self.base_url}/extract/task", headers=self.headers, json={"url": pdf_url, "model_version": model_version}))["task_id"]
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            task_data = self._check(self.session.get(f"{self.base_url}/extract/task/{task_id}", headers=self.headers))
            state = task_data.get("state", "")
            if state == "done":
                break
            if state == "failed":
                raise Exception(f"解析失败: {task_data.get('err_msg', '未知错误')}")
            time.sleep(5)
        else:
            raise Exception(f"等待超时，超过{max_wait}秒")
        
        if "full_zip_url" not in task_data:
            return None
        
        os.makedirs(output_dir, exist_ok=True)
        zip_path = os.path.join(output_dir, task_data["full_zip_url"].split("/")[-1].split("?")[0])
        extract_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(zip_path))[0])
        
        res = self.session.get(task_data["full_zip_url"], headers={"Authorization": self.headers["Authorization"]}, stream=True)
        res.raise_for_status()
        with open(zip_path, 'wb') as f:
            for chunk in res.iter_content(8192):
                if chunk:
                    f.write(chunk)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
        
        md_files = list(Path(extract_dir).glob("**/*.md"))
        return md_files[0].read_text(encoding='utf-8') if md_files else None


if __name__ == "__main__":
    # 使用示例
    client = PDFMinerUClient()  # 使用默认token，或传入自定义token: PDFMinerUClient(token="your_token")
    pdf_url = "https://cdn-mineru.openxlab.org.cn/demo/example.pdf"
    md_content = client.extract(pdf_url=pdf_url, output_dir="./output")
    if md_content:
        print(f"解析完成，MD内容长度: {len(md_content)} 字符")
        print(f"前500字符预览:\n{md_content[:500]}")
    else:
        print("解析失败或未找到MD文件")
