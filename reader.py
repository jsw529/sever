import streamlit as st
import requests

st.title("📖 PPT + 대본 읽어주는 AI 웹사이트")

# 서버 URL
SERVER_URL = "http://localhost:8000"

# --- 대본 업로드 ---
uploaded_script = st.file_uploader("대본 (.txt) 파일 업로드", type=["txt"])

script_text = ""
if uploaded_script:
    script_text = uploaded_script.read().decode("utf-8")
    st.text_area("대본 미리보기", script_text, height=200)

# --- PPT 업로드 (선택사항) ---
uploaded_ppt = st.file_uploader("PPT (.pptx) 파일 업로드 (선택)", type=["pptx"])
if uploaded_ppt:
    with st.spinner("PPT 파일에서 텍스트 추출 중..."):
        files = {"file": uploaded_ppt.getvalue()}
        res = requests.post(f"{SERVER_URL}/upload_ppt", files={"file": uploaded_ppt})
        if res.status_code == 200:
            ppt_text = res.json()["text"]
            st.text_area("PPT 추출 텍스트", ppt_text, height=200)
            script_text = ppt_text  # PPT 내용으로 덮어쓰기
        else:
            st.error("PPT 텍스트 추출 실패!")

# --- 목소리 선택 ---
st.subheader("목소리 선택")
voices = []
selected_voice = ""
try:
    res = requests.get(f"{SERVER_URL}/voices")
    if res.status_code == 200:
        voices = res.json()
        korean_voices = [v for v in voices if "ko-KR" in v["language_codes"]]
        if korean_voices:
            selected_voice = st.selectbox(
                "원하는 목소리를 선택하세요",
                options=[v["name"] for v in korean_voices]
            )
except:
    st.error("목소리 리스트를 불러올 수 없습니다. 서버 확인하세요!")

# --- 오디오 생성 및 재생 ---
if st.button("🗣️ 읽기 시작"):
    if not script_text:
        st.warning("대본을 업로드하거나 작성해 주세요.")
    else:
        with st.spinner("AI가 읽는 중입니다..."):
            res = requests.post(
                f"{SERVER_URL}/synthesize",
                data={"text": script_text, "voice_name": selected_voice}
            )
            if res.status_code == 200:
                audio_bytes = res.content
                st.audio(audio_bytes, format="audio/mp3")
            else:
                st.error("음성 생성 실패!")

