# Ai Foundation - Architecture

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Overview

Core ai services including llm routing, rag pipeline, and embeddings.


## Components

### Core Components

- **LLM Router (Claude, GPT-4, Gemini)**
- **RAG Pipeline with Qdrant vector DB**
- **Embeddings generation**
- **Prompt template management**
- **Model abstraction layer**

## Technology Stack

- Python 3.11+
- FastAPI (if service)
- PostgreSQL (Supabase)
- Redis (EventBus)

## Integration Points

### Internal Dependencies

- `shared.database` - Database client
- `shared.eventbus` - Event messaging

### External Dependencies

- Supabase PostgreSQL
- Redis
- AI APIs (Anthropic, OpenAI)

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
- Review Date: 2025-10-09
