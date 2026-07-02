import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

# 💡 ChromaDB 라이브러리 임포트
import chromadb

load_dotenv()

app = FastAPI()
client = genai.Client()

# =====================================================================
# 🗄️ [RAG 초기화 영역] 문서 로드 및 임베딩 공간(Vector DB) 생성
# =====================================================================
# 내장형 메모리 크로마 클라이언트 생성
chroma_client = chromadb.Client()
# 'my_knowledge'라는 이름의 벡터 창고(Collection) 생성
collection = chroma_client.get_or_create_collection(name="my_knowledge")

# 서버 시작 시 지식 문서(knowledge.txt)를 읽어서 벡터 창고에 넣는 함수
def initialize_rag():
    if not os.path.exists("knowledge.txt"):
        print("⚠️ knowledge.txt 파일이 없어 RAG 초기화를 건너뜁니다.")
        return

    with open("knowledge.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # 문서를 줄 바꿈 단위로 쪼갭니다 (간단한 Chunking)
    chunks = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 각 청크(문단)를 벡터 창고에 저장합니다.
    # chromadb는 기본적으로 내장 임베딩 모델(all-MiniLM-L6-v2)을 사용해 자동으로 수치화합니다.
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"doc_chunk_{i}"]
        )
    print(f"✅ RAG 초기화 완료: {len(chunks)}개의 지식 조각을 Vector DB에 저장했습니다.")

# FastAPI 시작 이벤트 때 RAG 초기화 실행
@app.on_event("startup")
def startup_event():
    initialize_rag()

# =====================================================================
# ⚙️ [비즈니스 로직 및 엔드포인트]
# =====================================================================
class ChatMessage(BaseModel):
    message: str

def ask_gemini_with_rag(user_text: str, max_retries=3, retry_delay=1.5):
    # 1. 사용자의 질문과 가장 유사한 문서 조각을 Vector DB에서 2개 검색합니다 (Retrieval)
    results = collection.query(
        query_texts=[user_text],
        n_results=2
    )
    
    # 검색된 문서 조각들을 하나의 텍스트로 합칩니다.
    retrieved_docs = "\n".join(results['documents'][0]) if results['documents'] else "참고할 문서가 없습니다."
    
    # 2. AI에게 줄 프롬프트를 조립합니다. (지식 조각을 Context로 제공)
    # 이것이 RAG의 핵심인 프롬프트 인젝션(Prompt Injection)입니다.
    system_instruction = f"""당신은 회사의 인프라 지원실 지식 기반 어시스턴트입니다.
반드시 아래 제공된 [참고 문서]의 내용에만 기반하여 사용자의 질문에 정확하고 친절하게 답변하세요.
만약 문서에 없는 내용이거나 알 수 없는 내용이라면, 모른다고 정직하게 답하세요.

[참고 문서]
{retrieved_docs}"""

    # 3. Gemini에게 프롬프트를 던져 답변을 생성합니다 (Generation)
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_text,
                # config를 통해 시스템 지침(참고 문서 포함)을 주입합니다.
                config={"system_instruction": system_instruction}
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

@app.post("/api/chat")
async def chat_endpoint(payload: ChatMessage):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")
    
    ai_response = ask_gemini_with_rag(payload.message)
    return {"reply": ai_response}

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

app.mount("/", StaticFiles(directory="static"), name="static")