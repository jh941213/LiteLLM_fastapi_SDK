# 필요한 모듈과 클래스 임포트
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from app.core.config import settings
from pydantic import validator

# 메시지 역할을 정의하는 열거형 클래스
class Role(str, Enum):
    USER = "user"          # 사용자 역할
    ASSISTANT = "assistant"  # AI 어시스턴트 역할
    SYSTEM = "system"      # 시스템 역할

# 채팅 메시지 스키마 정의
class Message(BaseModel):
    role: Role      # 메시지 작성자의 역할
    content: str    # 메시지 내용

# 채팅 완성 요청 스키마 정의
class ChatCompletionRequest(BaseModel):
    model: str      # 사용할 AI 모델
    messages: List[Message]  # 대화 메시지 목록
    stream: Optional[bool] = False  # 스트리밍 응답 여부
    temperature: Optional[float] = settings.DEFAULT_TEMPERATURE  # 응답의 창의성 정도
    max_tokens: Optional[int] = settings.DEFAULT_MAX_TOKENS  # 최대 토큰 수
    
    # temperature 값 검증 메서드
    @validator('temperature')
    def validate_temperature(cls, v, values):
        model = values.get('model')
        if model and v is not None:
            limits = settings.MODEL_LIMITS.get(model, {})
            temp_range = limits.get('temperature_range', (0.0, 1.0))
            if not (temp_range[0] <= v <= temp_range[1]):
                raise ValueError(f"temperature는  {temp_range[0]}과 {temp_range[1]} 사이여야 합니다")
        return v

    # max_tokens 값 검증 메서드
    @validator('max_tokens')
    def validate_max_tokens(cls, v, values):
        model = values.get('model')
        if model and v is not None:
            limits = settings.MODEL_LIMITS.get(model, {})
            max_limit = limits.get('max_tokens', 2000)
            if v > max_limit:
                raise ValueError(f"max_tokens는 {max_limit}을 초과할 수 없습니다")
        return v

# AI 모델 정보 스키마 정의
class ModelInfo(BaseModel):
    id: str         # 모델 식별자
    object: str = "model"  # 객체 타입
    owned_by: str   # 모델 제공 업체

# 제목 요약 요청 스키마 정의
class TitleSummaryRequest(BaseModel):
    content: str    # 요약할 내용
    model: str = "openai/gpt-4o-mini"  # 기본 사용 모델
    max_tokens: Optional[int] = 50      # 최대 토큰 수 (기본값 50)
    temperature: Optional[float] = 0.1   # 응답의 창의성 정도 (기본값 0.1)