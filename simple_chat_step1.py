import os
from google import genai
from dotenv import load_dotenv

# 1. .env 파일에 저장된 API 키를 시스템 환경변수로 로드합니다.
load_dotenv()

# 2. Gemini 클라이언트를 초기화합니다.
# (API 키를 명시하지 않으면 자동으로 환경변수의 GEMINI_API_KEY를 찾습니다.)
client = genai.Client()

print("🤖 Gemini 챗봇 맛보기 테스트를 시작합니다! (종료하려면 '종료' 입력)")
print("-" * 50)

while True:
    # 3. 사용자로부터 콘솔 입력을 받습니다.
    user_input = input("나: ")
    
    # 종료 조건 처리
    if user_input.strip() == "종료":
        print("🤖 챗봇을 종료합니다. 다음에 또 만나요!")
        break
        
    if not user_input.strip():
        continue

    try:
        # 4. Gemini 모델에게 메시지를 보내고 답변을 받습니다.
        # 가장 가볍고 빠른 gemini-2.5-flash 모델을 사용합니다.
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_input,
        )
        # 5. AI의 답변을 화면에 출력합니다.
        print(f"Gemini: {response.text}")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ 에러가 발생했습니다: {e}")