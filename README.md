# AI 기반 LLM API 서비스

## 소개

다중 LLM(Large Language Model) 서비스를 통합 제공하는 FastAPI 기반 백엔드 서버입니다.

## 주요 기능

- 다중 LLM 모델 지원
  - Anthropic Claude
  - OpenAI GPT-4
  - Google Gemini
- 자동 폴백 시스템 (Claude → GPT-4 → Gemini)
- 스트리밍 응답 지원
- 제목 생성 서비스
- API 상태 모니터링

## 기술 스택

- Python 3.9+
- FastAPI
- litellm (LLM 통합 라이브러리)
- Pydantic
- Docker

## 시작하기

### 요구사항

- Python 3.9 이상
- pip
- Docker & Docker Compose (선택사항)

### 설치

```bash
git clone https://github.com/your-username/ai-api.git
cd ai-api
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 환경 설정

1. `.env.example` 파일을 `.env`로 복사
2. 필요한 API 키 설정:
   - ANTHROPIC_API_KEY
   - OPENAI_API_KEY
   - GEMINI_API_KEY

### 실행 방법

개발 환경:
```bash
uvicorn app.main:app --reload
```

Docker 환경:
```bash
docker-compose up -d
```

## API 엔드포인트

### 채팅 완성 API
```bash
POST /v1/chat/completions
```

요청 예시:
```json
{
    "model": "anthropic/claude-3-5-sonnet-20240620",
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ],
    "stream": false,
    "temperature": 0.1,
    "max_tokens": 2000
}
```

### 모델 목록 조회
```bash
GET /v1/models
```

### 서버 상태 확인
```bash
GET /health
```

### 제목 생성
```bash
POST /v1/title/summary
```

## 프로젝트 구조

```
ai-api/
├── app/
│   ├── api/
│   │   └── main.py        # FastAPI 애플리케이션 설정
│   ├── core/
│   │   └── config.py      # 환경 설정 및 상수
│   ├── routers/
│   │   └── api.py         # API 라우터 및 엔드포인트
│   ├── schemas/
│   │   └── schema.py      # Pydantic 모델
│   └── services/
│       └── service.py     # 비즈니스 로직
├── tests/                 # 테스트 코드
├── .env.example          # 환경 변수 템플릿
└── requirements.txt      # 의존성 패키지
```

### 주요 모듈 설명

- **main.py**: FastAPI 애플리케이션 초기화 및 CORS 설정
- **config.py**: 환경 변수, 모델 제한사항, 기본 설정값 관리
- **api.py**: API 엔드포인트 정의 및 요청 처리
- **schema.py**: 데이터 모델 및 유효성 검증
- **service.py**: LLM 통합 및 비즈니스 로직 구현

## 지원 모델

- Anthropic Claude 3.5 Sonnet
- OpenAI GPT-4o Mini
- Google Gemini 1.5 Pro

각 모델은 고유한 토큰 제한과 temperature 범위를 가지고 있습니다.

## 테스트

### 채팅 완성 API
```bash
POST /v1/chat/completions
```

요청 예시:
```json
{
    "model": "anthropic/claude-3-5-sonnet-20240620",
    "messages": [
        {
            "role": "system",
            "content": "당신은 도움이 되는 AI 어시스턴트입니다."
        },
        {
            "role": "user",
            "content": "안녕하세요, 오늘 날씨는 어떤가요?"
        }
    ],
    "stream": false,
    "temperature": 0.1,
    "max_tokens": 2000
}
```

응답 예시:
```json
{
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "죄송하지만 저는 실시간 날씨 정보에 접근할 수 없습니다. 현재 날씨를 확인하시려면 날씨 앱이나 기상청 웹사이트를 확인해보시는 것을 추천드립니다."
            }
        }
    ]
}
```

### 모델 목록 조회
```bash
GET /v1/models
```

응답 예시:
```json
{
    "data": [
        {
            "id": "anthropic/claude-3-5-sonnet-20240620",
            "object": "model",
            "owned_by": "anthropic"
        },
        {
            "id": "openai/gpt-4o-mini",
            "object": "model",
            "owned_by": "openai"
        },
        {
            "id": "gemini/gemini-1.5-pro",
            "object": "model",
            "owned_by": "google"
        }
    ]
}
```

### 서버 상태 확인
```bash
GET /health
```

응답 예시:
```json
{
    "status": "healthy",
    "api_keys": {
        "anthropic": true,
        "openai": true,
        "gemini": true
    },
    "models": [
        "anthropic/claude-3-5-sonnet-20240620",
        "openai/gpt-4o-mini",
        "gemini/gemini-1.5-pro"
    ]
}
```

### 제목 생성
```bash
POST /v1/title/summary
```

요청 예시:
```json
{
    "content": "이 서비스는 사용자의 일정을 관리하고 알림을 제공하는 캘린더 애플리케이션입니다. 사용자는 일정을 추가, 수정, 삭제할 수 있으며 다른 사용자와 일정을 공유할 수도 있습니다.",
    "model": "openai/gpt-4o-mini",
    "temperature": 0.1,
    "max_tokens": 50
}
```

응답 예시:
```json
{
    "title": "스마트 일정관리 캘린더"
}
```



MIT License