# 필요한 타입과 클래스 임포트
from typing import Dict, ClassVar
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    # API 키 환경변수 설정
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # 기본 설정값
    DEFAULT_MAX_TOKENS: int = 2000  # 기본 최대 토큰 수
    DEFAULT_TEMPERATURE: float = 0.1  # 기본 온도(창의성) 설정
    
    # 각 모델별 제한사항 설정
    MODEL_LIMITS: ClassVar[Dict[str, Dict]] = {
        "anthropic/claude-3-5-sonnet-20240620": {
            "max_tokens": 4096,  # 최대 토큰 제한
            "temperature_range": (0.0, 1.0)  # 온도 범위
        },
        "openai/gpt-4o-mini": {
            "max_tokens": 2048,
            "temperature_range": (0.0, 2.0)
        },
        "gemini/gemini-1.5-pro": {
            "max_tokens": 2048,
            "temperature_range": (0.0, 1.0)
        }
    }
    
    # 모델별 제공 업체 매핑
    MODEL_CONFIGS: ClassVar[Dict[str, str]] = {
        "anthropic/claude-3-5-sonnet-20240620": "anthropic",
        "openai/gpt-4o-mini": "openai", 
        "gemini/gemini-1.5-pro": "google"
    }

# Settings 클래스의 인스턴스 생성
settings = Settings()