import streamlit as st
import openai

# API 키 설정 (보안을 위해 코드에 직접 적기보다 환경변수 사용 권장)
# 만약 오류가 나면 openai.api_key = "본인의_API_KEY" 를 여기에 넣으세요
openai.api_key = "여기에_OPENAI_API_KEY_입력"

st.title("📈 AI 차트 & 뉴스 통합 분석기")
st.write("차트 이미지를 드래그 앤 드롭으로 업로드하고 분석을 시작하세요.")

# 1. 파일 업로더 (드래그 앤 드롭 지원)
uploaded_file = st.file_uploader("차트 이미지 업로드", type=["png", "jpg", "jpeg"])
ticker = st.text_input("종목명 (예: NVDA, 005930.KS)")

# 2. 분석 실행 로직
if st.button("분석 실행"):
    if uploaded_file is None or not ticker:
        st.warning("이미지와 종목명을 모두 입력해주세요!")
    else:
        with st.spinner('AI가 차트와 뉴스를 분석 중입니다...'):
            try:
                # 이미지 보여주기
                st.image(uploaded_file, caption='업로드된 차트', use_container_width=True)
                
                # 분석 메시지 구성 (이미지 데이터는 바이너리로 전송)
                st.info("분석 중... 잠시만 기다려주세요.")
                
                # 실제 분석 요청
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "당신은 전문 주식 분석가입니다. 업로드된 차트 이미지의 패턴(지지/저항/추세)을 분석하고, 사용자가 입력한 종목의 현재 시장 상황과 결합하여 투자 의견을 제시하세요."},
                        {"role": "user", "content": [
                            {"type": "text", "text": f"이 차트를 분석하고 {ticker}의 향후 방향성을 예측해줘."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{uploaded_file.getvalue().hex()}"}}
                        ]}
                    ]
                )
                
                # 결과 출력
                st.subheader("💡 AI 분석 결과")
                st.write(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")