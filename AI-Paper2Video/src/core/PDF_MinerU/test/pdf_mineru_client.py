#!/usr/bin/env python3
"""MinerU PDF解析客户端"""

import requests
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MinerUClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://mineru.net/api/v4"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def create_extract_task(self, pdf_url, model_version="vlm", **kwargs):
        """创建PDF解析任务"""
        data = {"url": pdf_url, "model_version": model_version}
        for key in ['enable_formula', 'enable_table', 'language', 'page_ranges', 'is_ocr', 'data_id']:
            if key in kwargs:
                data[key] = kwargs[key]
        
        response = requests.post(f"{self.base_url}/extract/task", headers=self.headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result["code"] != 0:
            raise Exception(f"创建任务失败: {result.get('msg', '未知错误')}")
        
        return {"task_id": result["data"]["task_id"]}
    
    def get_task_result(self, task_id, max_wait_time=600, check_interval=5):
        """获取解析任务结果"""
        url = f"{self.base_url}/extract/task/{task_id}"
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            if result["code"] != 0:
                raise Exception(f"查询失败: {result.get('msg', '未知错误')}")
            
            task_data = result["data"]
            state = task_data.get("state", "")
            
            if state == "done":
                return result
            elif state == "failed":
                raise Exception(f"解析失败: {task_data.get('err_msg', '未知错误')}")
            elif state == "running":
                progress = task_data.get("extract_progress", {})
                print(f"解析中... {progress.get('extracted_pages', 0)}/{progress.get('total_pages', 0)} 页")
            
            time.sleep(check_interval)
        
        raise Exception(f"等待超时，超过{max_wait_time}秒")
    
    def download_result(self, zip_url, output_dir="."):
        """下载解析结果（修复：添加Authorization header）"""
        os.makedirs(output_dir, exist_ok=True)
        filename = zip_url.split("/")[-1].split("?")[0]  # 移除查询参数
        output_path = os.path.join(output_dir, filename)
        
        # 关键修复：使用Authorization header下载
        headers = {"Authorization": f"Bearer {self.token}"}
        
        session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        
        response = session.get(zip_url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        print(f"\r下载进度: {downloaded*100//total_size}%", end='', flush=True)
        
        print(f"\n下载完成: {output_path}")
        return output_path