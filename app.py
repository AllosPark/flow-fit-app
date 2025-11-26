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
        model = "gemini-2.0-flash"
        
        prompt = f"""
        You are 'Flow Fit', an expert personal trainer.
        User Condition: {condition}
        Target Muscle: {target_muscle}
        
        Create a specific workout routine.
        Return ONLY a JSON array. Do not include markdown formatting (```json).
        Format: [{{"exercise": "Name", "sets": "Number of sets, e.g., 4", "reps": "Range, e.g., 10-12", "tip": "Short Korean tip"}}]
        """
        
        # AI에게 JSON 형식으로 데이터를 요청
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
    
    # '루틴 생성하기' 버튼이 눌렸을 때
    if st.button("루틴 생성하기 (Start)"):
        with st.spinner("AI 트레이너가 루틴을 짜고 있습니다..."):
            routine_data = get_workout_routine(target, condition)
            st.session_state['routine'] = routine_data
            
            # --- [기능 추가] 세트 기록 초기화 ---
            st.session_state['tracking'] = {}
            for item in routine_data:
                st.session_state['tracking'][item['exercise']] = 0 # 각 운동의 완료 세트를 0으로 초기화

# 메인 화면 결과 표시
if 'routine' in st.session_state and st.session_state['routine']:
    # tracking 상태가 없으면 초기화 (예외 방지)
    if 'tracking' not in st.session_state:
         st.session_state['tracking'] = {}
    
    st.success(f"✅ {condition} 컨디션에 맞춘 추천 루틴입니다!")
    
    # 카드 레이아웃
    for item in st.session_state['routine']:
        ex_name = item['exercise']
        
        # 'sets' 값을 정수로 파싱 (예: "4" -> 4)
        try:
            target_sets = int(item['sets'])
        except ValueError:
            target_sets = 4 # 파싱 에러 시 기본값 4
        
        current_sets = st.session_state['tracking'].get(ex_name, 0)
        progress = current_sets / target_sets if target_sets > 0 else 0
        
        # Expander 제목을 진행 상황으로 표시
        with st.expander(f"🏋️ {ex_name} ({current_sets}/{target_sets} 세트 완료)", expanded=True):
            
            # --- [기능 추가] 진행도 막대 ---
            st.progress(progress)
            
            col1, col2, col3 = st.columns([1.5, 1.5, 1])
            with col1:
                st.metric("목표 횟수(Reps)", item['reps'])
            with col2:
                st.metric("목표 세트(Total)", f"{target_sets} 세트")
            
            with col3:
                button_key = f"btn_{ex_name.replace(' ', '_')}"
                
                if current_sets < target_sets:
                    # '세트 완료' 버튼
                    if st.button(f"세트 완료 ✅", key=button_key):
                        # 완료 세트 수 증가
                        st.session_state['tracking'][ex_name] = current_sets + 1
                        # 화면을 새로고침하여 업데이트된 상태 반영
                        st.rerun() 
                else:
                    st.success("운동 완료! 🎉")

            st.info(f"💡 **Coach Tip:** {item['tip']}")

else:
    st.info("👈 왼쪽 사이드바에서 정보를 입력하고 버튼을 눌러주세요.")
