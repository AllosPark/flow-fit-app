import streamlit as st
from google import genai
from google.genai import types
import json
import time

# --- 1. Custom CSS 및 공통 디자인 (Figma Design Implementation) ---
st.markdown("""
<style>
/* 전체 다크 모드 배경 및 폰트 */
.stApp {
    background-color: #1a1a1a; 
    color: #f0f0f0; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
/* 컨테이너 및 카드 배경 */
.stContainer, .st-emotion-cache-zt5ig {
    background-color: #2b2b2b;
    border-radius: 12px;
}
/* 네온 그린 버튼 스타일 */
.stButton>button {
    background-color: #39FF14 !important; /* 네온 그린 */
    color: #1a1a1a !important;
    border-radius: 8px;
    font-weight: bold;
    border: none !important;
    transition: background-color 0.3s;
}
/* 버튼 호버 효과 */
.stButton>button:hover {
    background-color: #2cce0f !important; 
}
/* 🎯 운동 메트릭 박스 스타일 (Image 2) */
.metric-box {
    background-color: #3a3a3a;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    color: #f0f0f0;
    margin-bottom: 10px;
}
.metric-value {
    font-size: 1.2em;
    font-weight: bold;
    color: #39FF14;
}
.metric-label {
    font-size: 0.8em;
    color: #b0b0b0;
}
/* Image 3 컨디션 카드 스타일 */
.condition-card {
    background-color: #2b2b2b;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    cursor: pointer;
    border: 1px solid #3a3a3a;
    transition: border-color 0.3s;
}
.condition-card:hover {
    border-
