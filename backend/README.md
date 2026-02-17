# AI Podcast Platform - Backend

Backend API for the AI Podcast Platform, built with FastAPI and Python.

## Features

- Text extraction from PDF, DOCX, and URLs
- AI-powered scenario generation
- TTS integration with multiple providers
- Audio processing and mixing
- Image generation for podcast covers
- RSS feed generation
- Podcast export to various platforms

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Server    │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   TTS Services  │
                    │   (OpenAI,     │
                    │    ElevenLabs)  │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   AI Services   │
                    │   (OpenAI GPT)  │
                    └─────────────────┘
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for deployment)
- PostgreSQL 15+
- Redis 7+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the development server:
```bash
uvicorn app.main:app --reload
```

### Development

The backend follows a modular structure:

```
app/
├── api/              # API endpoints
├── models/           # Database models
├── services/         # Business logic services
├── schemas/          # Pydantic models for validation
└── config.py         # Configuration settings
```

### API Endpoints

- `/api/text/` - Text extraction endpoints
- `/api/scenario/` - AI scenario generation
- `/api/tts/` - Text-to-speech endpoints
- `/api/audio/` - Audio processing endpoints
- `/api/image/` - Image generation endpoints
- `/api/rss/` - RSS feed generation
- `/api/export/` - Podcast export endpoints
- `/api/podcasts/` - Podcast management

### Testing

Run tests with:
```bash
pytest
```

### Deployment

For production deployment, use Docker Compose:
```bash
docker-compose up -d
```

## Configuration

Environment variables are managed through `.env` file. Key variables include:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - OpenAI API key
- `ELEVENLABS_API_KEY` - ElevenLabs API key
- `SECRET_KEY` - Application secret key

## License

MIT License