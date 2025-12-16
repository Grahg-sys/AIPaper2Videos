#!/usr/bin/env python3
"""
MinerU PDF解析示例脚本（URL方式）
演示如何使用MinerUClient类通过URL方式解析PDF并获取结果
"""

import os
import sys
from pdf_mineru_client import MinerUClient


def example_usage():
    """
    示例用法 - 使用URL方式
    """
    # 直接设置API token
    token = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiIzMzEwNjY5MSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2NTg4OTE1NCwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiIiwib3BlbklkIjpudWxsLCJ1dWlkIjoiMTE3MzczNGEtNDUzNy00ZDZhLWI4OGItNThhYmFmNmExZmI2IiwiZW1haWwiOiIiLCJleHAiOjE3NjcwOTg3NTR9.eu6mbKibIIJEPNP14JOPKFMFZnrjQfE1YtRyanZaJ0M3xH6oS28L8S0Na8C839BN9H_WyFDAtjbIVhxFAyUBCQ"
    
    # 创建客户端
    client = MinerUClient(token)
    
    # PDF文件URL - 使用官方示例PDF
    pdf_url = "https://cdn-mineru.openxlab.org.cn/demo/example.pdf"
    
    try:
        print("=== MinerU PDF解析示例 (URL方式) ===")
        print(f"PDF URL: {pdf_url}")
        
        # 步骤1: 创建解析任务
        print("\n1. 创建解析任务...")
        task_result = client.create_extract_task(
            pdf_url=pdf_url,
            model_version="vlm",  # 使用VLM模型
            enable_formula=True,  # 启用公式识别
            enable_table=True,    # 启用表格识别
            language="en"       # 中文文档
        )
        
        task_id = task_result["task_id"]
        print(f"   任务ID: {task_id}")
        
        # 步骤2: 等待解析完成
        print("\n2. 等待解析完成...")
        result = client.get_task_result(
            task_id=task_id,
            max_wait_time=600,  # 最多等待10分钟
            check_interval=5    # 每5秒检查一次
        )
        
        # 步骤3: 下载解析结果
        print("\n3. 下载解析结果...")
        task_data = result["data"]
        
        if task_data.get("state") == "done":
            print("   文件解析完成!")
            
            if "full_zip_url" in task_data:
                # 下载结果
                zip_path = client.download_result(
                    task_data["full_zip_url"], 
                    output_dir="./output"
                )
                
                # 解压结果到当前文件夹
                import zipfile
                import shutil
                
                # 获取当前脚本所在目录
                current_dir = os.path.dirname(os.path.abspath(__file__))
                extract_dir = os.path.join(current_dir, "extracted_results")
                
                # 如果目录已存在，先删除
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)
                
                # 创建新目录并解压
                os.makedirs(extract_dir)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                print(f"   结果已解压到: {extract_dir}")
                
                # 显示结果文件列表
                print("\n   解析结果文件:")
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, extract_dir)
                        print(f"     - {rel_path}")
        
        elif task_data.get("state") == "failed":
            error_msg = task_data.get("err_msg", "未知错误")
            print(f"   文件解析失败: {error_msg}")
        
        print("\n=== 任务完成! ===")
        
    except Exception as e:
        print(f"错误: {e}")


def test_with_custom_url():
    """
    使用自定义URL进行测试
    """
    # 直接设置API token
    token = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiIzMzEwNjY5MSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2NTg4OTE1NCwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiIiwib3BlbklkIjpudWxsLCJ1dWlkIjoiMTE3MzczNGEtNDUzNy00ZDZhLWI4OGItNThhYmFmNmExZmI2IiwiZW1haWwiOiIiLCJleHAiOjE3NjcwOTg3NTR9.eu6mbKibIIJEPNP14JOPKFMFZnrjQfE1YtRyanZaJ0M3xH6oS28L8S0Na8C839BN9H_WyFDAtjbIVhxFAyUBCQ"
    
    # 创建客户端
    client = MinerUClient(token)
    
    # 你可以在这里修改为自己的PDF URL
    custom_pdf_url = input("请输入PDF文件的URL (直接回车使用官方示例): ").strip()
    if not custom_pdf_url:
        custom_pdf_url = "https://cdn-mineru.openxlab.org.cn/demo/example.pdf"
    
    try:
        print(f"\n使用URL: {custom_pdf_url}")
        
        # 创建解析任务
        task_result = client.create_extract_task(
            pdf_url=custom_pdf_url,
            model_version="vlm",
            enable_formula=True,
            enable_table=True,
            language="ch"
        )
        
        # 等待解析完成
        result = client.get_task_result(task_result["task_id"])
        
        # 下载并解压结果到当前文件夹
        task_data = result["data"]
        if task_data.get("state") == "done" and "full_zip_url" in task_data:
            zip_path = client.download_result(task_data["full_zip_url"], "./output")
            
            # 解压结果到当前文件夹
            import zipfile
            import shutil
            
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            extract_dir = os.path.join(current_dir, "extracted_results_custom")
            
            # 如果目录已存在，先删除
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            
            # 创建新目录并解压
            os.makedirs(extract_dir)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            print(f"结果已下载到: {zip_path}")
            print(f"结果已解压到: {extract_dir}")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 运行基本示例
    example_usage()
    
    # 如果你想测试自定义URL，可以取消下面的注释
    # print("\n" + "="*50)
    # test_with_custom_url()