import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = genai.Client()

# 1. 사용자가 보낼 데이터 구조 정의 (포맷 검증용)
class ChatMessage(BaseModel):
    message: str

# 2. 진짜 Gemini API와 통신하는 핵심 비즈니스 로직
def ask_gemini_with_retry(user_text: str, max_retries=3, retry_delay=1.5):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_text,
            )
            return response.text
        except APIError as e:
            if e.code in [503, 429] and attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise HTTPException(status_code=500, detail=f"Gemini API Error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected Error: {e}")
    raise HTTPException(status_code=503, detail="Gemini 서비스가 일시적으로 불가능합니다.")

# 3. 브라우저에서 메시지를 보낼 API 엔드포인트
@app.post("/api/chat")
async def chat_endpoint(payload: ChatMessage):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")
    
    # Gemini에게 물어보고 답변 받기
    ai_response = ask_gemini_with_retry(payload.message)
    return {"reply": ai_response}

# 4. 프론트엔드 정적 파일(HTML/CSS/JS) 서빙 설정
# 루트(/) 주소로 접속하면 index.html을 보여줍니다.
@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

# 나머지 정적 파일(style.css, app.js)들을 자동으로 매핑합니다.
app.mount("/", StaticFiles(directory="static"), name="static")