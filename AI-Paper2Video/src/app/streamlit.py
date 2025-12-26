import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import time
import io
import base64
from datetime import datetime
import json
import os

# 设置页面配置 - 现代极简风格
st.set_page_config(
    page_title="Paper2Videos - AI学术视频生成",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 现代极简设计
st.markdown("""
<style>
    /* 全局样式 - 现代极简背景 */
    .stApp {
        background: linear-gradient(135deg, #fafbfc 0%, #f1f3f4 100%);
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        color: #1a1a1a;
    }
    
    /* 标题样式 - 极简现代 */
    .main-title {
        text-align: center;
        color: #0d0d0d;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #0d0d0d 0%, #4a4a4a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 400;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }
    
    /* 卡片样式 - 极简现代 */
    .upload-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(20px);
        animation: fadeIn 0.8s ease-out 0.4s both;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .upload-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 1.8rem;
        margin: 1rem 0;
        box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.6s ease-out both;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        background: rgba(255, 255, 255, 0.95);
        animation: float 2s ease-in-out infinite;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.8s ease;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    /* 按钮样式 - 现代极简 */
    .stButton > button {
        background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        letter-spacing: 0.01em;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        animation: pulse 1.5s infinite;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s ease;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* 次要按钮样式 */
    .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.9);
        color: #374151;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-color: rgba(0, 0, 0, 0.15);
    }
    
    /* 进度条样式 - 现代极简 */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #0d0d0d 0%, #374151 100%);
        border-radius: 4px;
        height: 6px;
    }
    
    /* 文件上传区域 - 现代极简 */
    .uploadedFile {
        border: 2px dashed #d1d5db;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.6);
        padding: 2.5rem;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .uploadedFile:hover {
        background: rgba(255, 255, 255, 0.8);
        border-color: #9ca3af;
        transform: scale(1.01);
        animation: pulse 2s infinite;
    }
    
    .uploadedFile::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        transition: left 0.8s ease;
    }
    
    .uploadedFile:hover::before {
        left: 100%;
    }
    
    /* 加载动画 */
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-top: 3px solid #0d0d0d;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* 侧边栏样式 - 现代极简 */
    .css-1d391kg {
        background: rgba(248, 250, 252, 0.95);
        border-right: 1px solid rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(20px);
    }
    
    /* 指标卡片 - 现代极简 */
    .metric-card {
        background: linear-gradient(135deg, #0d0d0d 0%, #1f2937 100%);
        color: white;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(20px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        font-family: 'SF Pro Display', sans-serif;
    }
    
    .metric-label {
        font-size: 0.8rem;
        opacity: 0.8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* 输入框样式 - 现代极简 */
    .stTextInput > div > div > input {
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.9);
        transition: all 0.2s ease;
        font-size: 0.95rem;
        padding: 0.6rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(0, 0, 0, 0.3);
        box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
        background: rgba(255, 255, 255, 1);
    }
    
    /* 选择框样式 */
    .stSelectbox > div > div > div {
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.9);
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div > div:hover {
        border-color: rgba(0, 0, 0, 0.2);
        background: rgba(255, 255, 255, 1);
    }
    
    /* 多选框样式 */
    .stMultiSelect > div > div > div {
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* 滑块样式 */
    .stSlider > div > div > div {
        background: #0d0d0d;
        border-radius: 4px;
    }
    
    .stSlider > div > div {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 4px;
    }
    
    /* 单选按钮样式 */
    .stRadio > div > div > label > div:first-child {
        background: #0d0d0d;
        border-radius: 50%;
    }
    
    /* 复选框样式 */
    .stCheckbox > div > div > label > div:first-child {
        background: #0d0d0d;
        border-radius: 4px;
    }
    
    /* 警告框样式 */
    .stWarning {
        background: rgba(254, 243, 199, 0.8);
        border: 1px solid rgba(251, 191, 36, 0.3);
        border-radius: 12px;
        color: #92400e;
        backdrop-filter: blur(10px);
    }
    
    /* 成功提示样式 */
    .stSuccess {
        background: rgba(209, 250, 229, 0.8);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        color: #065f46;
        backdrop-filter: blur(10px);
    }
    
    /* 信息提示样式 */
    .stInfo {
        background: rgba(219, 234, 254, 0.8);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        color: #1e40af;
        backdrop-filter: blur(10px);
    }
    
    /* 动画效果 - 现代极简 */
    @keyframes fadeInDown {
        0% {
            opacity: 0;
            transform: translateY(-20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        0% {
            opacity: 0;
            transform: translateY(20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        0% {
            opacity: 0;
            transform: scale(0.98);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes slideInLeft {
        0% {
            opacity: 0;
            transform: translateX(-30px);
        }
        100% {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        0% {
            opacity: 0;
            transform: translateX(30px);
        }
        100% {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        50% {
            transform: scale(1.02);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -200% 0;
        }
        100% {
            background-position: 200% 0;
        }
    }
    
    @keyframes float {
        0% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-5px);
        }
        100% {
            transform: translateY(0px);
        }
    }
    
    /* 展开面板样式 */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(10px);
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.95);
        border-color: rgba(0, 0, 0, 0.12);
    }
    
    /* 代码块样式 */
    .stCodeBlock {
        background: rgba(249, 250, 251, 0.9);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* 表格样式 */
    table {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    th {
        background: rgba(249, 250, 251, 0.9);
        color: #111827;
        font-weight: 600;
        padding: 1rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    }
    
    td {
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);
        color: #374151;
        padding: 1rem;
    }
    
    /* 滚动条样式 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.02);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 4px;
        transition: all 0.2s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 0, 0, 0.3);
    }
    
    /* 标题样式 */
    h1, h2, h3, h4, h5, h6 {
        color: #0d0d0d;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* 段落样式 */
    p {
        color: #4b5563;
        line-height: 1.6;
    }
    
    /* 链接样式 */
    a {
        color: #0d0d0d;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: #374151;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'current_pdf' not in st.session_state:
    st.session_state.current_pdf = None
if 'video_url' not in st.session_state:
    st.session_state.video_url = None
if 'history' not in st.session_state:
    st.session_state.history = []

# 主界面 - 现代极简标题
st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1 style='color: #0d0d0d; font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem; letter-spacing: -0.02em; background: linear-gradient(135deg, #0d0d0d 0%, #4a4a4a 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>Paper2Videos</h1>
        <p style='color: #6b7280; font-size: 1.2rem; font-weight: 400; margin-top: 0.5rem;'>AI驱动的学术文献视频生成工具</p>
    </div>
""", unsafe_allow_html=True)

# 侧边栏 - 现代极简风格
with st.sidebar:
    st.markdown("""
        <div style='margin-bottom: 2rem; animation: slideInLeft 0.6s ease-out;'>
            <h3 style='color: #0d0d0d; font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em;'> 快速导航</h3>
        </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "",
        ["📄 上传文献", "⚙️ 参数设置", "🎥 视频生成", "📚 历史记录"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("""
        <div style='margin: 2rem 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent);'></div>
    """, unsafe_allow_html=True)
    
    # 统计信息 - 现代极简卡片
    st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h4 style='color: #0d0d0d; font-size: 1rem; font-weight: 700; margin-bottom: 1rem; letter-spacing: -0.01em;'>📊 使用统计</h4>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0d0d0d 0%, #1f2937 100%); color: white; border-radius: 12px; padding: 1.2rem; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.1); backdrop-filter: blur(20px);'>
            <div style='font-size: 2rem; font-weight: 700; margin-bottom: 0.2rem; font-family: "SF Pro Display", sans-serif;'>{len(st.session_state.history)}</div>
            <div style='font-size: 0.8rem; opacity: 0.8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;'>总生成数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        today_count = sum(1 for h in st.session_state.history if datetime.now().strftime('%Y-%m-%d') in h.get('timestamp', ''))
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0d0d0d 0%, #1f2937 100%); color: white; border-radius: 12px; padding: 1.2rem; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.1); backdrop-filter: blur(20px);'>
            <div style='font-size: 2rem; font-weight: 700; margin-bottom: 0.2rem; font-family: "SF Pro Display", sans-serif;'>{today_count}</div>
            <div style='font-size: 0.8rem; opacity: 0.8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;'>今日生成</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='margin: 2rem 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent);'></div>
    """, unsafe_allow_html=True)
    
    # 功能特色 - 现代极简图标
    st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h4 style='color: #0d0d0d; font-size: 1rem; font-weight: 700; margin-bottom: 1rem; letter-spacing: -0.01em;'>✨ 功能特色</h4>
        </div>
    """, unsafe_allow_html=True)
    
    features = [
        "🎯 智能内容提取",
        "🎨 多种视频风格", 
        "⚡ 快速生成",
        "🔧 自定义参数",
        "📱 高清输出"
    ]
    
    for feature in features:
        st.markdown(f"""
        <div style='display: flex; align-items: center; margin: 0.8rem 0; padding: 0.5rem 0; border-radius: 8px; transition: all 0.2s ease;'>
            <span style='margin-right: 0.8rem; font-size: 1.1rem;'>{feature.split(' ')[0]}</span>
            <span style='color: #374151; font-size: 0.9rem; font-weight: 500;'>{' '.join(feature.split(' ')[1:])}</span>
        </div>
        """, unsafe_allow_html=True)

# 页面1: 上传文献 - 现代极简风格
if page == "📄 上传文献":
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 2.5rem; margin-bottom: 2rem; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06); border: 1px solid rgba(0, 0, 0, 0.08); backdrop-filter: blur(20px);'>
            <h2 style='color: #0d0d0d; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.01em;'>📤 上传您的学术文献</h2>
            <p style='color: #6b7280; font-size: 1rem; margin-bottom: 2rem;'>支持 PDF 格式，文件大小不超过 50MB</p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        # 文件上传区域
        uploaded_file = st.file_uploader(
            "",
            type=['pdf'],
            help="请上传您想要转换为视频的学术文献",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # 保存文件信息
            st.session_state.current_pdf = {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 显示文件信息 - 现代极简风格
            st.markdown(f"""
                <div style='background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 1.2rem; margin: 1.5rem 0;'>
                    <div style='display: flex; align-items: center; margin-bottom: 0.8rem;'>
                        <span style='color: #065f46; font-size: 1.2rem; margin-right: 0.5rem;'>✅</span>
                        <span style='color: #065f46; font-weight: 600;'>文件上传成功</span>
                    </div>
                    <div style='color: #374151; font-size: 0.9rem; line-height: 1.5;'>
                        <strong>文件名:</strong> {uploaded_file.name}<br>
                        <strong>文件大小:</strong> {uploaded_file.size / 1024 / 1024:.2f} MB<br>
                        <strong>上传时间:</strong> {st.session_state.current_pdf['upload_time']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # 文件预览 - 现代极简风格
            with st.expander("📖 文件预览"):
                st.markdown("""
                    <div style='background: rgba(249, 250, 251, 0.9); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 12px; padding: 1.5rem; margin-top: 1rem;'>
                        <h4 style='color: #0d0d0d; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;'>文档结构预览</h4>
                        <div style='color: #374151; font-size: 0.95rem; line-height: 1.6;'>
                            <div style='margin-bottom: 0.8rem;'><strong style='color: #0d0d0d;'>📑 标题:</strong> 基于深度学习的计算机视觉研究</div>
                            <div style='margin-bottom: 0.8rem;'><strong style='color: #0d0d0d;'>👥 作者:</strong> 张三, 李四, 王五</div>
                            <div style='margin-bottom: 0.8rem;'><strong style='color: #0d0d0d;'>🏢 机构:</strong> 清华大学人工智能研究院</div>
                            <div style='margin-bottom: 0.8rem;'><strong style='color: #0d0d0d;'>📅 发表时间:</strong> 2024年</div>
                            <div><strong style='color: #0d0d0d;'>📊 页数:</strong> 15页</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h3 style='color: #0d0d0d; font-size: 1.4rem; font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em;'>🎯 支持的文献类型</h3>
            </div>
        """, unsafe_allow_html=True)
        
        paper_types = [
            {"icon": "🔬", "type": "研究论文", "desc": "学术论文、期刊文章"},
            {"icon": "📚", "type": "综述文献", "desc": "文献综述、调研报告"},
            {"icon": "🎓", "type": "学位论文", "desc": "硕士、博士论文"},
            {"icon": "⚗️", "type": "实验报告", "desc": "实验研究、技术报告"}
        ]
        
        for paper in paper_types:
            st.markdown(f"""
                <div style='background: rgba(255, 255, 255, 0.9); border-radius: 16px; padding: 1.8rem; margin: 1rem 0; box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04); border: 1px solid rgba(0, 0, 0, 0.06); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);'>
                    <div style='display: flex; align-items: center; margin-bottom: 0.8rem;'>
                        <span style='font-size: 1.5rem; margin-right: 0.8rem;'>{paper['icon']}</span>
                        <h4 style='color: #0d0d0d; font-size: 1.1rem; font-weight: 600; margin: 0;'>{paper['type']}</h4>
                    </div>
                    <p style='color: #6b7280; font-size: 0.9rem; margin: 0; line-height: 1.5;'>{paper['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# 页面2: 参数设置 - 现代极简风格
elif page == "⚙️ 参数设置":
    if st.session_state.current_pdf is None:
        st.warning("⚠️ 请先上传PDF文献")
        st.stop()
    
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 2.5rem; margin-bottom: 2rem; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06); border: 1px solid rgba(0, 0, 0, 0.08); backdrop-filter: blur(20px);'>
            <h2 style='color: #0d0d0d; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.01em;'>⚙️ 视频生成参数设置</h2>
            <p style='color: #6b7280; font-size: 1rem; margin-bottom: 2rem;'>自定义您的视频生成参数，以获得最佳效果</p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        # 基础设置
        st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h4 style='color: #0d0d0d; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; letter-spacing: -0.01em;'>📐 基础设置</h4>
            </div>
        """, unsafe_allow_html=True)
        
        video_title = st.text_input(
            "视频标题",
            value=f"基于{st.session_state.current_pdf['name'].replace('.pdf', '')}的学术视频",
            help="为您的视频设置一个吸引人的标题"
        )
        
        video_duration = st.select_slider(
            "视频时长",
            options=["1分钟", "3分钟", "5分钟", "10分钟", "15分钟"],
            value="5分钟",
            help="根据文献内容复杂度选择合适的视频时长"
        )
        
        resolution = st.selectbox(
            "分辨率",
            ["1080p (1920x1080)", "720p (1280x720)", "4K (3840x2160)"],
            help="选择合适的视频分辨率"
        )
        
        aspect_ratio = st.radio(
            "画面比例",
            ["16:9 (横屏)", "9:16 (竖屏)", "1:1 (正方形)"],
            horizontal=True,
            help="根据发布平台选择合适的画面比例"
        )
        
        # 风格设置
        st.markdown("""
            <div style='margin: 2.5rem 0 1.5rem;'>
                <h4 style='color: #0d0d0d; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; letter-spacing: -0.01em;'>🎨 风格设置</h4>
            </div>
        """, unsafe_allow_html=True)
        
        video_style = st.selectbox(
            "视频风格",
            ["学术专业", "简洁现代", "生动活泼", "科技感", "商务正式"],
            help="选择视频的整体视觉风格"
        )
        
        color_scheme = st.color_picker(
            "主色调",
            "#4299e1",
            help="选择视频的主色调"
        )
        
        narration_tone = st.selectbox(
            "解说语调",
            ["专业严谨", "温和亲切", "活泼生动", "深沉磁性"],
            help="选择AI解说的语音语调"
        )
        
        background_music = st.checkbox(
            "添加背景音乐",
            value=True,
            help="为视频添加合适的背景音乐"
        )
        
        # 内容设置
        st.markdown("""
            <div style='margin: 2.5rem 0 1.5rem;'>
                <h4 style='color: #0d0d0d; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; letter-spacing: -0.01em;'>📝 内容设置</h4>
            </div>
        """, unsafe_allow_html=True)
        
        content_focus = st.multiselect(
            "内容重点",
            ["研究背景", "核心方法", "实验结果", "结论展望", "创新点"],
            default=["研究背景", "核心方法", "实验结果"],
            help="选择视频中要重点展示的内容"
        )
        
        animation_type = st.selectbox(
            "动画类型",
            ["渐进式", "翻页式", "淡入淡出", "滑动切换"],
            help="选择幻灯片切换的动画效果"
        )
        
        include_charts = st.checkbox(
            "包含图表动画",
            value=True,
            help="将文献中的图表转换为动画展示"
        )
        
        include_formulas = st.checkbox(
            "包含公式展示",
            value=True,
            help="将数学公式以动画形式展示"
        )
        
        language = st.selectbox(
            "输出语言",
            ["中文", "英文", "双语"],
            help="选择视频的语言"
        )
        
        # 保存设置
        if st.button("💾 保存设置", use_container_width=True):
            st.session_state.video_config = {
                'title': video_title,
                'duration': video_duration,
                'resolution': resolution,
                'aspect_ratio': aspect_ratio,
                'style': video_style,
                'color_scheme': color_scheme,
                'narration_tone': narration_tone,
                'background_music': background_music,
                'content_focus': content_focus,
                'animation_type': animation_type,
                'include_charts': include_charts,
                'include_formulas': include_formulas,
                'language': language
            }
            st.success("✅ 设置保存成功！")

# 页面3: 视频生成 - 现代极简风格
elif page == "🎥 视频生成":
    if st.session_state.current_pdf is None:
        st.warning("⚠️ 请先上传PDF文献")
        st.stop()
    
    if 'video_config' not in st.session_state:
        st.warning("⚠️ 请先设置视频参数")
        st.stop()
    
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 2.5rem; margin-bottom: 2rem; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06); border: 1px solid rgba(0, 0, 0, 0.08); backdrop-filter: blur(20px);'>
            <h2 style='color: #0d0d0d; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.01em;'>🎥 视频生成</h2>
            <p style='color: #6b7280; font-size: 1rem; margin-bottom: 2rem;'>AI驱动的智能视频生成</p>
    """, unsafe_allow_html=True)
    
    # 显示配置摘要
    with st.expander("📋 生成配置摘要"):
        config = st.session_state.video_config
        st.markdown(f"""
        <div style='background: rgba(249, 250, 251, 0.9); border: 1px solid rgba(0, 0, 0, 0.08); border-radius: 16px; padding: 2rem; margin: 1rem 0;'>
            <h4 style='color: #0d0d0d; font-size: 1.1rem; font-weight: 600; margin-bottom: 1.2rem; letter-spacing: -0.01em;'>📝 基本信息</h4>
            <div style='color: #374151; font-size: 0.95rem; line-height: 1.8; margin-bottom: 1.5rem;'>
                <div style='margin-bottom: 0.6rem;'><strong style='color: #0d0d0d;'>标题:</strong> {config['title']}</div>
                <div style='margin-bottom: 0.6rem;'><strong style='color: #0d0d0d;'>时长:</strong> {config['duration']}</div>
                <div style='margin-bottom: 0.6rem;'><strong style='color: #0d0d0d;'>分辨率:</strong> {config['resolution']}</div>
                <div><strong style='color: #0d0d0d;'>风格:</strong> {config['style']}</div>
            </div>
            
            <h4 style='color: #0d0d0d; font-size: 1.1rem; font-weight: 600; margin-bottom: 1.2rem; letter-spacing: -0.01em;'>🎨 视觉设置</h4>
            <div style='color: #374151; font-size: 0.95rem; line-height: 1.8; margin-bottom: 1.5rem;'>
                <div style='margin-bottom: 0.6rem;'><strong style='color: #0d0d0d;'>画面比例:</strong> {config['aspect_ratio']}</div>
                <div style='margin-bottom: 0.6rem;'><strong style='color: #0d0d0d;'>动画类型:</strong> {config['animation_type']}</div>
                <div><strong style='color: #0d0d0d;'>背景音乐:</strong> {'是' if config['background_music'] else '否'}</div>
            </div>
            
            <h4 style='color: #0d0d0d; font-size: 1.1rem; font-weight: 600; margin-bottom: 1.2rem; letter-spacing: -0.01em;'>📊 内容设置</h4>
            <div style='color: #374151; font-size: 0.95rem; line-height: 1.8;'>
                <div style='margin-bottom: 0.6rem;'><strong style='color: #0d0d0d;'>内容重点:</strong> {', '.join(config['content_focus'])}</div>
                <div style='margin-bottom: 0.6rem;'><strong style='color: #0d0d0d;'>解说语调:</strong> {config['narration_tone']}</div>
                <div><strong style='color: #0d0d0d;'>输出语言:</strong> {config['language']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 生成按钮
    st.markdown("""
        <div style='margin: 2.5rem 0; text-align: center;'>
            <h3 style='color: #0d0d0d; font-size: 1.4rem; font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em;'>🚀 开始生成视频</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎬 开始生成视频", use_container_width=True, disabled=st.session_state.processing):
            st.session_state.processing = True
            st.rerun()
    
    # 处理状态
    if st.session_state.processing:
        st.markdown("""
            <div style='margin: 2.5rem 0 1.5rem;'>
                <h3 style='color: #0d0d0d; font-size: 1.4rem; font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em;'>⏳ 正在生成视频...</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # 进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 模拟处理步骤
        steps = [
            ("📖 正在解析PDF内容...", 10),
            ("🔍 正在提取关键信息...", 25),
            ("📝 正在生成视频脚本...", 40),
            ("🎨 正在设计视觉元素...", 55),
            ("🎵 正在准备音频内容...", 70),
            ("🎬 正在合成视频...", 85),
            ("🔧 正在优化输出...", 95),
            ("✅ 视频生成完成！", 100)
        ]
        
        for i, (step_text, progress) in enumerate(steps):
            status_text.text(step_text)
            progress_bar.progress(progress)
            time.sleep(1.5)  # 模拟处理时间
        
        # 完成处理
        st.session_state.processing = False
        st.session_state.video_url = "generated_video.mp4"  # 模拟生成的视频
        
        # 添加到历史记录
        st.session_state.history.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pdf_name': st.session_state.current_pdf['name'],
            'video_title': st.session_state.video_config['title'],
            'status': 'completed'
        })
        
        st.success("🎉 视频生成成功！")
        st.balloons()
    
    # 显示生成的视频
    if st.session_state.video_url:
        st.markdown("""
            <div style='margin: 2.5rem 0 1.5rem;'>
                <h3 style='color: #0d0d0d; font-size: 1.4rem; font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em;'>🎥 生成的视频</h3>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1], gap="large")
        
        with col1:
            # 模拟视频播放器
            st.markdown("""
            <div style='background: linear-gradient(135deg, #0d0d0d 0%, #374151 100%); border-radius: 20px; padding: 3rem; text-align: center; color: white; margin: 1.5rem 0; box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>🎬</div>
                <h3 style='font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;'>视频预览</h3>
                <p style='color: rgba(255,255,255,0.8); margin-bottom: 1.5rem;'>您的视频已生成完成</p>
                <div style='background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; border: 1px solid rgba(255,255,255,0.1);'>
                    <div style='display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; color: rgba(255,255,255,0.9);'>
                        <span>时长: 5分钟</span>
                        <span>分辨率: 1080p</span>
                        <span>风格: 学术专业</span>
                    </div>
                </div>
                <p style='opacity: 0.6; font-size: 0.8rem;'>*此处将显示实际生成的视频播放器</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div style='margin-bottom: 2rem;'>
                    <h3 style='color: #0d0d0d; font-size: 1.4rem; font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em;'>📥 下载选项</h3>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("⬇️ 下载视频", use_container_width=True):
                st.success("📥 视频下载开始！")
            
            if st.button("📝 下载字幕", use_container_width=True):
                st.success("📄 字幕文件下载开始！")
            
            if st.button("📋 下载脚本", use_container_width=True):
                st.success("📄 视频脚本下载开始！")
            
            st.markdown("""
                <div style='margin: 2rem 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent);'></div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <div style='margin-bottom: 1.5rem;'>
                    <h3 style='color: #0d0d0d; font-size: 1.4rem; font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em;'>🔄 其他操作</h3>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("✏️ 重新编辑", use_container_width=True):
                st.session_state.video_url = None
                st.rerun()
            
            if st.button("🆕 生成新视频", use_container_width=True):
                st.session_state.current_pdf = None
                st.session_state.video_url = None
                if 'video_config' in st.session_state:
                    del st.session_state.video_config
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# 页面4: 历史记录
elif page == "📚 历史记录":
    st.markdown("""
        <div style='animation: fadeInDown 0.8s ease-out;'>
            <h2 style='color: #0d0d0d; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.01em;'>📚 生成历史</h2>
            <p style='color: #6b7280; font-size: 1rem; margin-bottom: 2rem;'>查看您的所有创作记录</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("📝 暂无生成记录，开始创建您的第一个视频吧！")
    else:
        # 搜索和筛选
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 搜索历史记录", placeholder="输入文件名或关键词")
        with col2:
            filter_type = st.selectbox("📅 筛选方式", ["全部", "今日", "本周", "本月"])
        
        # 显示历史记录
        for i, record in enumerate(reversed(st.session_state.history)):
            if search_term and search_term.lower() not in record['pdf_name'].lower() and search_term.lower() not in record['video_title'].lower():
                continue
                
            animation_delay = i * 0.1  # Staggered animation delay
                
            st.markdown(f"""
            <div class='feature-card' style='margin: 1rem 0; animation: slideInRight 0.6s ease-out {animation_delay}s both;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div style='flex: 1;'>
                        <h4 style='color: #0d0d0d; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;'>📄 {record['pdf_name']}</h4>
                        <p style='color: #6b7280; font-size: 0.9rem; margin-bottom: 0.3rem;'><strong>视频标题:</strong> {record['video_title']}</p>
                        <p style='color: #6b7280; font-size: 0.85rem; margin-bottom: 0.3rem;'><strong>生成时间:</strong> {record['timestamp']}</p>
                        <p style='color: #10b981; font-size: 0.85rem; font-weight: 500;'><strong>状态:</strong> ✅ 已完成</p>
                    </div>
                    <div style='display: flex; flex-direction: column; gap: 0.5rem;'>
                        <button style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 0.6rem 1.2rem; cursor: pointer; font-size: 0.85rem; font-weight: 500; transition: all 0.2s ease; box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);'>👁️ 查看</button>
                        <button style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; border-radius: 8px; padding: 0.6rem 1.2rem; cursor: pointer; font-size: 0.85rem; font-weight: 500; transition: all 0.2s ease; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);'>⬇️ 下载</button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 批量操作
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 清空历史记录", use_container_width=True):
                st.session_state.history = []
                st.success("✅ 历史记录已清空")
                st.rerun()
        
        with col2:
            if st.button("📊 导出记录", use_container_width=True):
                # 模拟导出功能
                st.success("📄 历史记录导出成功！")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255,255,255,0.7); padding: 2rem;'>
    <p>🎬 AI文献转视频平台 - 让学术研究更生动</p>
    <p style='font-size: 0.9rem;'>© 2024 AI Paper2Video. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)