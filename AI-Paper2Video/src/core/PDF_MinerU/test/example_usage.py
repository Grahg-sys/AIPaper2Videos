#!/usr/bin/env python3
"""MinerU PDF解析示例"""

import os
import zipfile
import shutil
from pdf_mineru_client import MinerUClient

TOKEN = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiIzMzEwNjY5MSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2NTg4OTE1NCwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiIiwib3BlbklkIjpudWxsLCJ1dWlkIjoiMTE3MzczNGEtNDUzNy00ZDZhLWI4OGItNThhYmFmNmExZmI2IiwiZW1haWwiOiIiLCJleHAiOjE3NjcwOTg3NTR9.eu6mbKibIIJEPNP14JOPKFMFZnrjQfE1YtRyanZaJ0M3xH6oS28L8S0Na8C839BN9H_WyFDAtjbIVhxFAyUBCQ"


def extract_zip(zip_path, extract_dir):
    """解压zip文件"""
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"结果已解压到: {extract_dir}")


def main(pdf_url=None):
    """主函数"""
    client = MinerUClient(TOKEN)
    #pdf_url = pdf_url or "https://cdn-mineru.openxlab.org.cn/demo/example.pdf"
    pdf_url = pdf_url or "https://arxiv.org/pdf/2512.19783"
    print(f"PDF URL: {pdf_url}")
    
    # 创建任务
    task = client.create_extract_task(
        pdf_url=pdf_url,
        model_version="vlm",
        enable_formula=True,
        enable_table=True,
        language="en"
    )
    print(f"任务ID: {task['task_id']}")
    
    # 等待完成
    result = client.get_task_result(task["task_id"], max_wait_time=600)
    task_data = result["data"]
    
    if task_data.get("state") != "done":
        raise Exception(f"解析失败: {task_data.get('err_msg', '未知错误')}")
    
    # 下载并解压
    if "full_zip_url" in task_data:
        zip_path = client.download_result(task_data["full_zip_url"], "./output")
        extract_dir = os.path.join(os.path.dirname(__file__), "extracted_results")
        extract_zip(zip_path, extract_dir)
        
        print("\n解析结果文件:")
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), extract_dir)
                print(f"  - {rel_path}")


if __name__ == "__main__":
    main()