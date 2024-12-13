from typing import AsyncGenerator, Optional  # 비동기 제너레이터와 옵셔널 타입 임포트
import litellm  # LLM 통합 라이브러리 임포트
import os  # 환경변수 관리를 위한 os 모듈 임포트
from app.schemas.schema import ChatCompletionRequest, TitleSummaryRequest  # 요청 스키마 임포트
from app.core.config import settings  # 설정 모듈 임포트
import json  # JSON 처리를 위한 모듈 임포트

# API 키 환경변수 설정 - 각 LLM 서비스 사용을 위한 인증키 설정
os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY  # Anthropic API 키 설정
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY  # OpenAI API 키 설정
os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY  # Gemini API 키 설정

# litellm의 디버깅 모드 활성화 - 상세 로그 출력
litellm.set_verbose = True

async def _try_completion(request: ChatCompletionRequest, model: str):
    """
    내부용 helper 함수: 단일 모델에 대한 완성 시도
    
    Args:
        request (ChatCompletionRequest): 채팅 완성 요청 객체
        model (str): 사용할 LLM 모델명
    
    Returns:
        LLM 응답 객체
    """
    try:
        # 요청 메시지를 LLM이 이해할 수 있는 형식으로 변환
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        print(f"Trying model {model} with messages: {messages}")
        
        # 스트리밍 모드인 경우
        if request.stream:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or settings.DEFAULT_MAX_TOKENS,
                stream=True
            )
            return response
        # 일반 응답 모드인 경우
        else:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or settings.DEFAULT_MAX_TOKENS
            )
            return response
    except Exception as e:
        print(f"모델 {model} 오류: {str(e)}")
        raise e  # 에러를 상위로 전파

async def process_chat_completion(request: ChatCompletionRequest):
    """
    채팅 완성 요청 처리 (폴백 로직 포함)
    
    Args:
        request (ChatCompletionRequest): 채팅 완성 요청 객체
    
    Returns:
        LLM 응답 객체 또는 None (모든 모델 실패 시)
    """
    # 폴백 순서: Claude -> GPT-4 -> Gemini
    models = [
        "anthropic/claude-3-sonnet",
        "openai/gpt-4",
        "google/gemini-pro"
    ]
    
    # 각 모델을 순차적으로 시도
    for model in models:
        try:
            return await _try_completion(request, model)
        except Exception as e:
            print(f"Model {model} failed: {str(e)}")
            continue
    
    return None  # 모든 모델이 실패한 경우

async def stream_chat_completion(request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
    """
    스트리밍 방식의 채팅 완성 처리 (폴백 포함)
    
    Args:
        request (ChatCompletionRequest): 채팅 완성 요청 객체
    
    Yields:
        str: 스트리밍 응답 데이터
    """
    request.stream = True  # 스트리밍 모드 강제 설정
    
    # 먼저 요청된 모델 시도
    try:
        response = await _try_completion(request, request.model)
        async for chunk in response:
            if chunk and hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                # choices[0].delta.content가 있는 경우만 처리
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk.choices[0].delta.content}}]}, ensure_ascii=False)}\n\n"
        print(f"스트리밍 성공 모델: {request.model}")
        # 스트리밍 종료 신호 전송
        yield "data: [DONE]\n\n"
        return
    except Exception as e:
        print(f"요청 모델 실패: {str(e)}")
    
    # 실패 시 다른 모델들 시도
    other_models = [model for model in settings.MODEL_CONFIGS.keys() if model != request.model]
    for model in other_models:
        try:
            response = await _try_completion(request, model)
            async for chunk in response:
                if chunk and hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    if chunk.choices[0].delta and chunk.choices[0].delta.content:
                        yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk.choices[0].delta.content}}]}, ensure_ascii=False)}\n\n"
            print(f"폴백 스트리밍 성공 모델: {model}")
            yield "data: [DONE]\n\n"
            return
        except Exception as e:
            continue
    
    # 모든 모델이 실패했을 때 에러 응답 전송
    error_response = {
        "error": {
            "message": "모든 모델이 응답하지 못했습니다",
            "type": "server_error",
            "code": 500
        }
    }
    yield f"data: {json.dumps(error_response, ensure_ascii=False)}\n\n"

async def generate_title_summary(request: TitleSummaryRequest) -> str:
    """
    서비스 내용을 바탕으로 제목 생성
    
    Args:
        request (TitleSummaryRequest): 제목 생성 요청 객체
    
    Returns:
        str: 생성된 제목
        
    Raises:
        Exception: 제목 생성 실패 시 발생하는 예외
    """
    try:
        # 시스템 프롬프트와 사용자 입력으로 메시지 구성
        messages = [
            {
                "role": "system",
                "content": "당신은 주어진 서비스 설명을 바탕으로 간결하고 매력적인 서비스 제목을 생성하는 전문가입니다. 15자 이내로 요약해주세요."
            },
            {
                "role": "user",
                "content": request.content
            }
        ]
        
        # LLM API 호출하여 제목 생성
        response = await litellm.acompletion(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"제목 생성 오류: {str(e)}")
        raise e