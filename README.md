# 🌙 Bedtime Story Generator

A professional, production-grade agentic AI pipeline designed to generate high-quality, child-safe bedtime stories for children aged 5–10.

![Bedtime Story Generator](screenshots/hero.png)

## 🚀 Overview

This project implements a **bounded LLM agent pipeline** that transforms simple user preferences into rich, structured narrative experiences. It uses a multi-stage architecture to ensure safety, alignment, and literary quality.

### Key Features

- **Multi-Agent Orchestration**: Controller, Normalizer, Planner, Storyteller, Judge, and Reviser agents working in sequence.
- **Deterministic Guardrails**: Zero-LLM validators for word count, character consistency, and genre drift.
- **Fail-Closed Safety**: Strict normalization of user input and judge-led revision loops ensure no unsafe content reaches the child.
- **Production-Ready Backend**: FastAPI with rate limiting, structured logging, and Pydantic validation.
- **Modern Frontend**: React + Vite interface showing the "thinking" (audit trail) behind each story.

## 🏗️ Architecture

The system follows a modular, pipe-and-filter architecture where each stage is handled by a specialized agent or validator.

```mermaid
graph TD
    User((User)) -->|Preferences| API[FastAPI]
    API -->|StoryRequest| Controller[Controller Agent]
    Controller -->|Sanitized Request| Normalizer[Normalizer Agent]
    Normalizer -->|Approved Request| Planner[Planner Agent]
    Planner -->|5-Beat Outline| Storyteller[Storyteller Agent]
  
    Storyteller -->|Draft Story| Validators[Deterministic Validators]
    Storyteller -->|Draft Story| Judge[LLM Judge]
  
    Validators --> Decision{Pass?}
    Judge --> Decision
  
    Decision -->|Yes| Approved[Approved Story]
    Decision -->|No| RevisionRoute{Revision Route}
    Decision -->|Max Revisions| Failed[Failed Validation]
  
    RevisionRoute -->|Quality/Logic| Reviser[Reviser Agent]
    RevisionRoute -->|Too Long| Compressor[Compressor Agent]
    RevisionRoute -->|Too Short| Expander[Expander Agent]
  
    Reviser --> Validators
    Compressor --> Validators
    Expander --> Validators
```

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, OpenAI API, Pydantic, SlowAPI.
- **Frontend**: React, Vite, CSS3.
- **Testing**: Pytest, HTTPX.
- **Tooling**: Python-dotenv, Pydantic-settings.

## 🚦 Getting Started (Easy Setup)

To run this project locally, follow these steps. You will need [Node.js](https://nodejs.org/) and [Python 3](https://www.python.org/) installed on your computer.

### 1. Set up your API Key
1. In the `backend` folder, find the file named `.env.example`.
2. Rename it to `.env`.
3. Open the file and paste your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_key_here
   ```

### 2. Start the Backend (The "Brain")
1. Open your terminal and navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the required tools:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   uvicorn app.api:app --reload
   ```
   *The backend is now running at http://localhost:8000*

### 3. Start the Frontend (The "Interface")
1. Open a **new** terminal window/tab.
2. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
3. Install the interface components:
   ```bash
   npm install
   ```
4. Start the app:
   ```bash
   npm run dev
   ```
   *The app is now running! Open the link shown in your terminal (usually http://localhost:5173).*

## 📖 Available Views

- **Reviewer View** ([http://localhost:5173/reviewer](http://localhost:5173/reviewer)): Full technical evaluation UI for interviewers/developers. Shows audit trails, judge scores, and validator results.
- **Kids View** ([http://localhost:5173/kids](http://localhost:5173/kids)): Simplified, child-friendly story experience. Shows only approved stories with gentle visuals.

## 🧪 Testing

```bash
cd backend
pytest
```

## 📖 Documentation

For deeper dives into the system design and policies, refer to the `docs/` directory:

- [System Design](docs/SYSTEM_DESIGN.md) — Detailed architecture and agent roles.
- [Prompt Design](docs/PROMPT_DESIGN.md) — Strategies used for LLM reliability.
- [Safety &amp; Guardrails](docs/SAFETY.md) — How we protect young readers.
- [API Reference](docs/API.md) — Endpoint documentation.
- [Test Plan](docs/TEST_PLAN.md) — Verification strategy.

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
