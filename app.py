import streamlit as st
from google import genai
from google.genai import types
import json

# 페이지 설정
st.set_page_config(page_title="Flow Fit AI", page_icon="💪", layout="wide")

# API 키 불러오기 (Secrets에서 가져옴)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # 키가 없을 때 화면에 에러 표시
    st.error("🚨 API 키를 찾을 수 없습니다! Streamlit 설정의 Secrets에 'GOOGLE_API_KEY'를 추가해주세요.")
    st.stop()

def get_workout_routine(target_muscle, condition):
    try:
        client = genai.Client(api_key=API_KEY)
        # 최신 모델 사용
        model = "gemini-2.0-flash"
        
        prompt = f"""
        You are 'Flow Fit', an expert personal trainer.
        User Condition: {condition}
        Target Muscle: {target_muscle}
        
        Create a specific workout routine.
        Return ONLY a JSON array. Do not include markdown formatting (```json).
        Format: [{{"exercise": "Name", "sets": "Number", "reps": "Range", "tip": "Short Korean tip"}}]
        """
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"AI 호출 중 오류 발생: {e}")
        return []

# --- UI 시작 ---
st.title("💪 Flow Fit: AI Personal Trainer")
st.markdown("### 당신의 컨디션에 맞는 최적의 루틴을 제안합니다.")

# 사이드바
with st.sidebar:
    st.header("오늘의 정보 입력")
    condition = st.selectbox("오늘 컨디션은?", ["최고예요! 😆", "보통이에요 🙂", "조금 피곤해요 😫", "부상이 있어요 🩹"])
    target = st.text_input("어디 운동 할까요?", "가슴, 삼두")
    
    if st.button("루틴 생성하기 (Start)"):
        with st.spinner("AI 트레이너가 루틴을 짜고 있습니다..."):
            routine_data = get_workout_routine(target, condition)
            st.session_state['routine'] = routine_data

# 메인 화면 결과 표시
if 'routine' in st.session_state and st.session_state['routine']:
    st.success(f"✅ {condition} 컨디션에 맞춘 추천 루틴입니다!")
    for item in st.session_state['routine']:
        with st.expander(f"🏋️ {item['exercise']} ({item['sets']} 세트)", expanded=True):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("횟수(Reps)", item['reps'])
            with col2:
                st.info(f"💡 **Tip:** {item['tip']}")
