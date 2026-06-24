# Specification: I'm a school psychologist, and I want to develop an AI-based report writer. There are many already on the market, but they are poor in quality. I can write better reports with my AI prompts, but I need a downloadable app to automate my workflow. I plan to give it away to other psychologists for free, and they will only have to pay the API fees. This project might be more collaborative than most, because it will be using AI prompts and other files that I have already written. I need a developer to build the application code, but almost all of the application's behavior — what it displays, how it processes data, what it sends to the LLM — is controlled through JSON config files and plain text prompt files. This will allow me to update the system without requiring code changes. I'm very passionate about this project and enjoy working with others, and I would be a very reliable collaborator. The app itself involves taking uploaded documents (mostly PDFs), and using LLM calls through AWS Bedrock to extract the relevant data. The user also enters a few decisions in the app, which uses all this information to generate a narrative. The user then reviews and edits the narrative, and the app exports a finished Word document based on a pre-written template. The extraction process already works very well in Claude — it reliably pulls the data I need from the PDFs and writes a high-quality narrative. For the app, I have developed a thorough blueprint that covers the architecture, data flow, feature specifications, and developer notes. The blueprint is detailed and specific, but I would always welcome a developer's perspective if they see a better way to implement something. The project would be built in phases, starting with the core pipeline. Required: Python, Qt (PySide6), experience building desktop applications, comfort working from a detailed blueprint. Nice to have: AWS Bedrock or boto3 experience, PDF processing, Word document generation (python-docx).

## 1. Project Overview

**Project:** I'm a school psychologist, and I want to develop an AI-based report writer. There are many already on the market, but they are poor in quality. I can write better reports with my AI prompts, but I need a downloadable app to automate my workflow. I plan to give it away to other psychologists for free, and they will only have to pay the API fees. This project might be more collaborative than most, because it will be using AI prompts and other files that I have already written. I need a developer to build the application code, but almost all of the application's behavior — what it displays, how it processes data, what it sends to the LLM — is controlled through JSON config files and plain text prompt files. This will allow me to update the system without requiring code changes. I'm very passionate about this project and enjoy working with others, and I would be a very reliable collaborator. The app itself involves taking uploaded documents (mostly PDFs), and using LLM calls through AWS Bedrock to extract the relevant data. The user also enters a few decisions in the app, which uses all this information to generate a narrative. The user then reviews and edits the narrative, and the app exports a finished Word document based on a pre-written template. The extraction process already works very well in Claude — it reliably pulls the data I need from the PDFs and writes a high-quality narrative. For the app, I have developed a thorough blueprint that covers the architecture, data flow, feature specifications, and developer notes. The blueprint is detailed and specific, but I would always welcome a developer's perspective if they see a better way to implement something. The project would be built in phases, starting with the core pipeline. Required: Python, Qt (PySide6), experience building desktop applications, comfort working from a detailed blueprint. Nice to have: AWS Bedrock or boto3 experience, PDF processing, Word document generation (python-docx).
**GitHub Repo:** https://github.com/9KMan/JOB-20260624141941-000106
**Lead:** 
**Client:** School psychologist (individual)
**Tier:** MICRO
**Budget:** $35-$50/hr
**Rate:** N/A
**Timeline:** 4-8 weeks

## 2. Technical Stack

Python · Desktop Application · API Integration · Natural Language Processing · Qt · PySide6 · AWS Bedrock · boto3 · PDF processing · python-docx

## 3. Architecture

- Backend: Python (FastAPI/Flask/Django) REST API
- Cloud: AWS (EC2, S3, Lambda, CloudFront)
- AI/ML: Model integration (OpenAI/Anthropic API or self-hosted)
- Data: ETL pipeline with task orchestration

### API Design
- RESTful endpoints with JSON request/response
- Authentication via JWT (HS256) or bcrypt
- Middleware for logging, error handling, CORS
- Versioned routes (/api/v1/...) where applicable

### Data Layer
- PostgreSQL as primary datastore
- Connection pooling via PGBouncer or similar
- Migration management via Alembic or raw SQL
- Indexes on foreign keys and high-cardinality columns

### Frontend (if applicable)
- Single-page application or server-rendered pages
- Responsive UI with modern CSS/JS framework
- State management for complex client-side logic

## 4. Data Model

### Core Entities
- Define entity schema based on job requirements
- Use UUIDs for primary keys (not auto-increment)
- Add created_at / updated_at timestamps to all tables
- Soft-delete pattern where appropriate

### Relationships
- Foreign key constraints with ON DELETE CASCADE
- Many-to-many via junction tables
- Eager loading for nested relationships in API

## 5. Project Structure

```
├── api/                  # FastAPI / Express routes + schemas
├── models/               # DB models / SQLAlchemy / Prisma
├── services/             # Business logic layer
├── workers/              # Background jobs (Celery, BullMQ, etc.)
├── migrations/           # DB migrations (Alembic / Flyway)
├── tests/                # Unit + integration tests
├── Dockerfile            # Production container
├── docker-compose.yml    # Local dev environment
└── README.md             # Setup instructions
```

## 6. Out of Scope

- Mobile apps (web only unless explicitly specified)
- Multi-tenant / white-label customization
- Performance optimization at 1M+ user scale

## 7. Acceptance Criteria

- [ ] REST API with all planned endpoints implemented and returning JSON
- [ ] Frontend UI implemented, responsive, and functional
- [ ] AI/ML pipeline integrated and functional
- [ ] AWS services configured per architecture
- [ ] ETL pipeline processing data end-to-end

**GitHub Repo:** https://github.com/9KMan/JOB-20260624141941-000106
