# FastAPI와 필요한 모듈 임포트
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.api import router

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="AI LLM API",  # API 제목
    description="Multi-LLM API with fallback support (Claude → GPT-4 → Gemini)",  # API 설명
    version="1.0.0"  # API 버전
)

# CORS 미들웨어 설정
# 모든 출처(*), 메서드, 헤더에 대한 접근 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청 허용
    allow_credentials=True,  # 인증 정보 포함 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# API 라우터 등록
app.include_router(router)

# 직접 실행 시 uvicorn 서버 구동
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",  # 실행할 애플리케이션 경로
        host="0.0.0.0",      # 모든 네트워크 인터페이스에서 접근 허용
        port=8000,           # 서버 포트 번호
        reload=True          # 코드 변경 시 자동 재시작 활성화
    )
