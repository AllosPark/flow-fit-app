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
    border-color: #39FF14;
}
.active-condition {
    border: 2px solid #39FF14 !important;
    box-shadow: 0 0 8px rgba(57, 255, 20, 0.4);
}
/* 채팅 UI 스타일링 */
.stChatMessage-stChatMessageAvatar-ai {
    background-color: #39FF14 !important;
    color: black !important;
}
.stChatMessage-stChatMessageContainer {
    background-color: #222222; /* 메시지 버블 배경 */
}
/* 하단 네비게이션 바 (고정) */
.footer-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    background-color: #222222;
    padding: 10px 0;
    display: flex;
    justify-content: space-around;
    align-items: center;
    border-top: 1px solid #333333;
    z-index: 1000;
    max-width: 420px; /* 모바일 폭 제한 */
    margin: auto;
}
.nav-item {
    text-align: center;
    color: #b0b0b0;
    font-size: 0.8em;
    cursor: pointer;
}
.nav-item.active {
    color: #39FF14;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- 2. 초기 설정 및 API 키 ---
st.set_page_config(page_title="Flow Fit AI", page_icon="💪", layout="wide")

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("🚨 API 키를 찾을 수 없습니다! Streamlit 설정의 Secrets에 'GOOGLE_API_KEY'를 추가해주세요.")
    st.stop()

# --- 3. 세션 상태 초기화 ---
if 'page' not in st.session_state: st.session_state['page'] = 'home'
if 'messages' not in st.session_state: 
    st.session_state['messages'] = [{"role": "ai", "content": "안녕하세요! 저는 AI 코치 FitPro입니다. 오늘 어떻게 도와드릴까요?"}]
if 'routine' not in st.session_state: st.session_state['routine'] = None
if 'tracking' not in st.session_state: st.session_state['tracking'] = {}
if 'current_condition' not in st.session_state: st.session_state['current_condition'] = '최고예요'


# --- 4. Gemini API 로직 ---
def get_workout_routine(target_muscle, condition):
    try:
        client = genai.Client(api_key=API_KEY)
        model = "gemini-2.0-flash"
        
        prompt = f"""
        You are 'Flow Fit', an expert personal trainer.
        User Condition: {condition}
        Target Muscle: {target_muscle}
        
        Create a specific workout routine. The target sets must be a single number (e.g., 4).
        Return ONLY a JSON array. Do not include markdown formatting (```json).
        Format: [{{"exercise": "Name", "sets": "Number", "reps": "Range", "weight": "e.g., 60kg", "tip": "Short Korean tip", "target": "e.g., 가슴"}}]
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

def process_user_input(user_input):
    if user_input:
        # 1. 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 2. AI에게 질문 (문맥 유지를 위해 전체 메시지 전달)
        try:
            client = genai.Client(api_key=API_KEY)
            api_messages = [{"role": m["role"], "parts": [{"text": m["content"]}]} 
                            for m in st.session_state.messages]
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=api_messages
            )
            ai_response = response.text
            
            # 3. AI 응답 추가
            st.session_state.messages.append({"role": "ai", "content": ai_response})
            
        except Exception as e:
             st.session_state.messages.append({"role": "ai", "content": f"🚨 죄송합니다. AI 코치 연결에 오류가 발생했습니다: {e}"})

# --- 5. 페이지 렌더링 함수 ---

# Image 3: 홈 (컨디션 선택) 페이지
def home_page():
    st.markdown('<h1 style="text-align: center; color: #f0f0f0; margin-bottom: 0;">Flow Fit</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #b0b0b0; margin-top: 5px;">AI 기반 퍼스널 코치</p>', unsafe_allow_html=True)
    
    st.markdown(f'<h3 style="text-align: center; color: #f0f0f0; margin-top: 40px;">오늘 컨디션은 <span style="color: #39FF14;">{st.session_state.current_condition}</span>이신가요?</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #b0b0b0;">AI 코치가 맞춤형 운동을 추천해드립니다</p>', unsafe_allow_html=True)

    conditions = [
        ("최고예요", "강한 운동 준비 완료", "⚡"),
        ("보통", "일반 에너지 수준", "📈"),
        ("피곤해요", "가벼운 운동 필요", "😴"),
        ("부상 있음", "수정된 루틴 필요", "🩹")
    ]
    
    # 컨디션 카드 구현 (CSS 기반)
    # Streamlit radio 버튼을 CSS와 함께 사용하여 컨디션 선택 및 상태 업데이트
    
    # 사용자가 현재 선택한 값을 저장
    current_choice = st.radio("컨디션 선택", [c[0] for c in conditions], index=0, label_visibility="collapsed", key='condition_radio_all')
    
    # CSS에서 active-condition을 적용하기 위해 숨겨진 HTML로 카드를 다시 그립니다.
    for name, desc, icon in conditions:
        is_active = current_choice == name
        card_html = f"""
        <div class="condition-card {'active-condition' if is_active else ''}" 
             data-condition="{name}"
             onclick="document.getElementById('condition-submit-{name}').click()">
            <p style="font-size: 1.1em; color: #f0f0f0;"><span style="font-size: 1.2em; margin-right: 10px;">{icon}</span> <strong>{name}</strong></p>
            <p style="color: #b0b0b0; font-size: 0.9em; margin-top: 5px;">{desc}</p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        # HTML 클릭 이벤트를 Streamlit 버튼 클릭으로 연결하는 숨겨진 버튼
        if st.button(f"선택 {name}", key=f'condition-submit-{name}', disabled=True):
            st.session_state['current_condition'] = name
            st.session_state['page'] = 'workout' 
            st.rerun()

    if st.button("내 맞춤 루틴 확인하기", use_container_width=True):
        st.session_state['current_condition'] = current_choice
        st.session_state['page'] = 'workout'
        st.rerun()

    # 하단 통계 박스 (Image 3)
    st.markdown('<div class="progress-stats-box">', unsafe_allow_html=True)
    cols = st.columns(3)
    stats = [("12", "연속 일수"), ("48", "총 운동"), ("92%", "목표 달성")]
    for i, (value, label) in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-box">
                <p class="metric-value">{value}</p>
                <p class="metric-label">{label}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# Image 2: 운동 (루틴 대시보드) 페이지
def workout_page():
    # 루틴이 없으면 새로 생성
    if st.session_state['routine'] is None:
        target = "가슴 & 삼두" # 임시 목표
        st.session_state['routine'] = get_workout_routine(target, st.session_state.current_condition)
        st.session_state['tracking'] = {} # 트래킹 초기화

    st.markdown(f'<h1 style="color: #f0f0f0;">오늘의 운동 루틴</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: #39FF14; font-size: 1.2em;">가슴 & 삼두 집중</p>', unsafe_allow_html=True)
    
    # 상단 요약 정보 (Image 2)
    col_summary = st.columns(3)
    with col_summary[0]: st.markdown('<p class="metric-label">⏰ 45-60분</p>', unsafe_allow_html=True)
    with col_summary[1]: st.markdown('<p class="metric-label">🏋️ 6개 운동</p>', unsafe_allow_html=True)
    with col_summary[2]: st.markdown('<p class="metric-label">🔥 420 kcal</p>', unsafe_allow_html=True)
    st.markdown('<hr style="border-top: 1px solid #3a3a3a;">', unsafe_allow_html=True)

    st.subheader("운동 계획")
    
    # 카드형 운동 리스트 및 세트 기록 구현
    for i, item in enumerate(st.session_state['routine']):
        ex_name = item['exercise']
        target_sets = int(item.get('sets', 4)) # sets 값 파싱, 에러 시 기본값 4
        current_sets = st.session_state['tracking'].get(ex_name, 0)
        
        # 각 운동을 별도의 컨테이너 (카드)로 묶음
        with st.container():
            st.markdown(f'<p style="font-size: 1.3em; color: #f0f0f0;">{ex_name}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: #b0b0b0; font-size: 0.8em; margin-top: -10px;">{item.get("target", "전신")}</p>', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            # 메트릭 박스 (세트, 횟수, 중량)
            with col1:
                st.markdown(f'<div class="metric-box"><p class="metric-label">세트</p><p class="metric-value">{current_sets}/{target_sets}</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-box"><p class="metric-label">횟수</p><p class="metric-value">{item["reps"]}</p></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-box"><p class="metric-label">중량</p><p class="metric-value">{item.get("weight", "자유")}</p></div>', unsafe_allow_html=True)
            
            with col4:
                # 세트 완료 버튼
                button_key = f"btn_{ex_name.replace(' ', '_')}_{i}"
                if current_sets < target_sets:
                    if st.button(f"세트 완료", key=button_key, use_container_width=True):
                        st.session_state['tracking'][ex_name] = current_sets + 1
                        st.rerun() 
                else:
                    st.markdown('<div style="text-align: center; padding-top: 15px;"><p style="color: #39FF14;">DONE! ✅</p></div>', unsafe_allow_html=True)
            
            st.markdown(f'<p style="color: #b0b0b0; margin-top: 5px;">💡 {item["tip"]}</p>', unsafe_allow_html=True)
            st.markdown('<hr style="border-top: 1px solid #3a3a3a; margin-top: 15px;">', unsafe_allow_html=True)
            
    # 하단 '운동 시작하기' 버튼 (Image 2)
    st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)
    if st.button("▶️ 운동 시작하기", key="start_workout_btn", use_container_width=True):
         st.balloons() # 완료 효과
         st.info("운동을 기록했습니다! 코치 페이지에서 조언을 구해보세요.")


# Image 1: 코치 (AI 채팅) 페이지
def coach_page():
    st.subheader("코치 FitPro")
    st.markdown('<div style="display: flex; align-items: center; gap: 8px;"><div style="width: 8px; height: 8px; background-color: #39FF14; border-radius: 50%;"></div><p style="color: #b0b0b0; font-size: 0.9em;">AI 어시스턴트 활성화</p></div>', unsafe_allow_html=True)

    # 📌 st.chat_message를 이용한 채팅 구현
    chat_container = st.container(height=400)
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="🤖" if message["role"] == "ai" else "👤"):
                st.markdown(message["content"])

    # 빠른 질문 버튼 구현 (Image 1)
    st.markdown('<p style="font-size: 0.9em; color: #b0b0b0; margin-top: 10px;">빠른 질문</p>', unsafe_allow_html=True)
    col_q = st.columns(3)
    quick_questions = ["허리 통증 운동", "벤치프레스 향상", "운동 후 식단"]
    
    for i, q in enumerate(quick_questions):
        with col_q[i]:
            if st.button(q, key=f"q_{i}", use_container_width=True):
                process_user_input(q)
                st.rerun()

    # 입력창 구현
    if user_input := st.chat_input("코치에게 질문하기..."):
        process_user_input(user_input)
        st.rerun()


# --- 6. 메인 앱 실행 및 라우팅 ---
def main_app():
    # 현재 페이지 내용 렌더링
    if st.session_state['page'] == 'home':
        home_page()
    elif st.session_state['page'] == 'workout':
        workout_page()
    elif st.session_state['page'] == 'coach':
        coach_page()
    elif st.session_state['page'] == 'profile':
        st.markdown("<h3>👤 프로필 페이지 (구현 예정)</h3>")

    # 하단 네비게이션 바 구현 (Figma 디자인 매칭)
    st.markdown("""
    <div class="footer-nav">
        <div class="nav-item" onclick="parent.postMessage({streamlit: 'set_page', page: 'home'}, '*')">🏠 홈</div>
        <div class="nav-item" onclick="parent.postMessage({streamlit: 'set_page', page: 'workout'}, '*')">🏋️ 운동</div>
        <div class="nav-item" onclick="parent.postMessage({streamlit: 'set_page', page: 'coach'}, '*')">💬 코치</div>
        <div class="nav-item" onclick="parent.postMessage({streamlit: 'set_page', page: 'profile'}, '*')">👤 프로필</div>
    </div>
    """, unsafe_allow_html=True)

    # JavaScript를 사용하여 Streamlit 상태를 변경하는 로직 (하단 네비게이션의 클릭 이벤트를 처리)
    js = f"""
    <script>
        const navItems = document.querySelectorAll('.footer-nav .nav-item');
        navItems.forEach(item => {{
            item.addEventListener('click', () => {{
                // Streamlit 버튼 클릭을 시뮬레이션
                const pageText = item.textContent.trim().split(' ')[1]; 
                const buttonId = pageText.toLowerCase() + '-hidden-btn';
                document.getElementById(buttonId).click();
            }});
        }});
    </script>
    """
    st.components.v1.html(js, height=0) 
    
    # 실제 Streamlit 상태를 바꾸기 위한 숨겨진 버튼 (JavaScript 클릭 시 작동)
    if st.button("홈", key="home-hidden-btn", help="Go Home", disabled=True):
        st.session_state['page'] = 'home'
        st.rerun()
    if st.button("운동", key="workout-hidden-btn", help="Go Workout", disabled=True):
        st.session_state['page'] = 'workout'
        st.rerun()
    if st.button("코치", key="coach-hidden-btn", help="Go Coach", disabled=True):
        st.session_state['page'] = 'coach'
        st.rerun()
    if st.button("프로필", key="profile-hidden-btn", help="Go Profile", disabled=True):
        st.session_state['page'] = 'profile'
        st.rerun()
    
    st.markdown('<style>button[disabled] { display: none; }</style>', unsafe_allow_html=True)


if __name__ == "__main__":
    main_app()
