# SI-EcoPass Backend

FastAPI backend service following Domain-Driven Design (DDD) principles.

## Features

- ✅ **Domain-Driven Design** architecture
- ✅ **Standardized API responses** (status, message, data)
- ✅ **Automatic Swagger documentation** at `/docs`
- ✅ **Type-safe** with Pydantic validation
- ✅ **Fast development** with `uv` package manager
- ✅ **Hot reload** in development mode

## Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run the application

```bash
# 개발 모드 (자동 리로드, 권장)
uv run fastapi dev src/main.py

# 또는 기존 방식
uv run python main.py

# 또는 프로덕션 모드
uv run fastapi run src/main.py
```

The API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Structure

```
src/
├── domain/          # Business logic core (entities, repositories)
├── application/     # Use cases and services
├── infrastructure/  # External integrations (DB, APIs)
├── api/            # HTTP endpoints and schemas
└── shared/         # Common utilities and schemas
```

## API Response Format

All endpoints return:

```json
{
  "status": "success" | "error",
  "message": "Human-readable message",
  "data": {...} | null
}
```

## Example API Usage

### Create an EcoPass

```bash
curl -X POST "http://localhost:8000/api/v1/ecopasses" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "title": "Green Commuter Pass",
    "description": "Pass for using public transportation"
  }'
```

### Get an EcoPass

```bash
curl "http://localhost:8000/api/v1/ecopasses/{ecopass_id}"
```

### Add Points

```bash
curl -X POST "http://localhost:8000/api/v1/ecopasses/{ecopass_id}/points" \
  -H "Content-Type: application/json" \
  -d '{"points": 50}'
```

## Development

See [CLAUDE.md](./CLAUDE.md) for detailed development guidelines and architecture documentation.

## Tech Stack

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **uv** - Fast package manager
- **Supabase** - Backend-as-a-service (planned)

## License

MIT
