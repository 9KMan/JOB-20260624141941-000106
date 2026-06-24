# Phase 5: Project Structure

## Phase Goal
Establish the directory layout, module boundaries, and file organization.

## Files to Create

```file:README.md
# # Python Desktop Application Developer — AI Report Writing T

**Built by: KMan | AI-Augmented Engineering Factory**

## Business Problem Solved
[Extract from SPEC.md — what pain point does this solve? Who benefits?]

## Quick Start
```
# Install
pip install -r requirements.txt  # or: npm install
cp .env.example .env

# Run
uvicorn app.main:app --reload  # or: npm run dev
```

## Tech Stack
Language:** Python 3.11+, GUI:** PySide6 (Qt for Python), LLM API:** AWS Bedrock (boto3), PDF Processing:** pypdf / pdfplumber, Word Generation:** python-docx, Config-Driven:** JSON config + plain-text prompt files, Distribution:** PyInstaller / briefcase for downloadable app

## Project Structure
```
# Add project structure here
```

## API Overview
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/health | Health check |

## Environment Variables
| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection string |
| SECRET_KEY | Application secret key |
```

## Done When
- README.md has 'Business Problem Solved' as first section
- README.md contains byline: '**Built by: KMan | AI-Augmented Engineering Factory**'
- Quick Start section is runnable without errors
