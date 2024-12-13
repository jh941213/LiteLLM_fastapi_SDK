# 필요한 모듈과 클래스 임포트
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.schemas.schema import ChatCompletionRequest, TitleSummaryRequest
from app.services.service import process_chat_completion, stream_chat_completion, generate_title_summary
from app.core.config import settings

# API 라우터 인스턴스 생성
router = APIRouter()

@router.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    채팅 완성 API 엔드포인트
    - Stream 및 Non-Stream 응답 지원
    - 자동 폴백: Claude → GPT-4 → Gemini
    """
    # 스트리밍 요청인 경우
    if request.stream:
        return StreamingResponse(
            stream_chat_completion(request),
            media_type="text/event-stream"
        )
    
    # 일반 요청 처리
    response = await process_chat_completion(request)
    if not response:
        raise HTTPException(
            status_code=500, 
            detail="All models failed to respond"
        )
    
    return response

@router.get("/v1/models")
async def list_models():
    """사용 가능한 모델 목록 조회"""
    # 설정된 모든 모델의 정보를 리스트로 반환
    return {
        "data": [
            {
                "id": model,
                "object": "model",
                "owned_by": settings.MODEL_CONFIGS[model]
            }
            for model in settings.MODEL_CONFIGS.keys()
        ]
    }

@router.get("/health")
async def health():
    """서버 상태 확인 엔드포인트"""
    # API 키 존재 여부와 사용 가능한 모델 목록 반환
    return {
        "status": "healthy",
        "api_keys": {
            "anthropic": bool(settings.ANTHROPIC_API_KEY),
            "openai": bool(settings.OPENAI_API_KEY),
            "gemini": bool(settings.GEMINI_API_KEY)
        },
        "models": list(settings.MODEL_CONFIGS.keys())
    }

@router.post("/v1/title/summary")
async def create_title_summary(request: TitleSummaryRequest):
    """서비스 설명을 바탕으로 제목 생성"""
    try:
        # 제목 생성 서비스 호출
        title = await generate_title_summary(request)
        return {"title": title}
    except Exception as e:
        # 에러 발생 시 500 에러 반환
        raise HTTPException(
            status_code=500,
            detail=f"제목 생성 실패: {str(e)}"
        )

