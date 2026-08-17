# DSTRAIX AI Assistant

A full-stack AI assistant powered by Google Gemini, featuring streaming chat, an AI agent with function calling, a local calculator for fast arithmetic, conversation memory, and document-grounded Q&A (RAG) via Gemini File Search.

Built with a **React** frontend, a **FastAPI** backend, and **Docker** for deployment.

---

## Features

- **Intelligent Chat** — Context-aware conversations with streaming responses for immediate feedback.
- **AI Agent** — Uses Gemini function calling to select and execute tools, then synthesizes a final answer from the results.
- **Local Calculator** — Detects simple arithmetic and evaluates it locally (via Python AST parsing, not `eval`) instead of routing it through the LLM, cutting latency and API calls.
- **Document RAG** — Upload documents and ask questions grounded in their content using Gemini File Search.
- **Conversation Memory** — Maintains session context so follow-up questions resolve correctly.
- **Modern Web UI** — Separate Chat, Agent, and Document modes with streaming display, upload handling, and responsive layout.

---

## Architecture

```
                     React Frontend
                            │
                          HTTP
                            │
                     FastAPI Backend
              ┌─────────────┼─────────────┐
              │             │             │
            Chat          Agent       Documents
              │             │             │
        Gemini Streaming  Gemini +    File Search
                         Function Calling
                          (Calculator,
                          other tools)
```

**Request flow examples:**

- **Chat:** `User → POST /chat/stream → Gemini → streamed chunks → UI`
- **Agent:** `User → POST /agent/ → Gemini selects a tool → tool executes → Gemini generates final response`
- **Calculator:** Simple arithmetic is detected and computed locally; anything more complex is routed to Gemini.
- **Document RAG:** `Upload → File Search indexing → question → relevant passages retrieved → grounded Gemini answer`

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, FastAPI, Pydantic, Uvicorn, Google GenAI SDK |
| Frontend | React, Vite, JavaScript, CSS |
| AI | Google Gemini (streaming, function calling, File Search) |
| Infrastructure | Docker, Docker Compose |

---

## Project Structure

```
DSTRAIX-AI-ASSISTANT/
├── backend/
│   ├── app/
│   │   ├── api/            # chat.py, documents.py, agent.py
│   │   ├── core/           # config.py
│   │   ├── memory/         # conversation.py
│   │   ├── schemas/        # chat.py
│   │   ├── services/       # llm_service.py, agent_service.py
│   │   ├── tools/          # calculator.py
│   │   └── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js and npm
- Docker
- A Google Gemini API key

### Backend Setup

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DSTRAIX-AI-ASSISTANT/backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows

pip install -r requirements.txt
```

Create `backend/.env`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### Frontend Setup

```bash
cd ../frontend
npm install
```

Create `frontend/.env`:

```
VITE_API_URL=http://127.0.0.1:8000
```

Run the frontend:

```bash
npm run dev
```

App will be available at `http://localhost:5173`.

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/chat/` | POST | Generate a complete (non-streamed) chat response |
| `/chat/stream` | POST | Stream a chat response incrementally |
| `/chat/{conversation_id}` | DELETE | Clear a conversation's history |
| `/agent/` | POST | Send a task to the AI agent |
| `/documents/store` | POST | Create a Gemini File Search store |
| `/documents/upload` | POST | Upload and index a document |
| `/documents/list` | GET | List indexed documents |
| `/documents/ask` | POST | Ask a question grounded in uploaded documents |

**Example — streaming chat:**

```json
POST /chat/stream
{
  "message": "What is machine learning?",
  "conversation_id": "conversation-123"
}
```

**Example — agent:**

```json
POST /agent/
{
  "message": "Calculate 125 * 48"
}
```

---

## Docker

**Build and run manually:**

```bash
docker build -t dstraix-backend ./backend
docker run --env-file backend/.env -p 8000:8000 dstraix-backend
```

**Or with Docker Compose:**

```bash
docker compose up --build
docker compose down
```

---

## Testing

| Test | Input | Expected Result |
|---|---|---|
| Normal chat | "What is machine learning?" | Streamed, coherent answer |
| Conversation memory | "My name is Alex." → "What is my name?" | "Your name is Alex." |
| Calculator | "Calculate 125 * 48" | Returns 6000, notably faster than an LLM round trip |
| Agent | "Explain how function calling works in AI agents." | Agent routes the request and returns a generated explanation |
| Document RAG | Upload a PDF → "What is this document about?" | Grounded answer based on retrieved content |
| Clear conversation | Click "Clear Chat" | History resets; new conversation can begin |

---

## Security Notes

- API keys are stored in environment variables, not hardcoded.
- `.env` files are excluded from version control; `.env.example` templates are provided.

For production deployment, additionally implement authentication, authorization, rate limiting, request validation, HTTPS, structured logging, and monitoring.

---

## Roadmap

- **Auth & multi-user support:** login, JWT auth, per-user conversations
- **Persistent memory:** PostgreSQL/Redis-backed storage in place of in-memory history
- **Advanced RAG:** multiple knowledge bases, metadata filtering, hybrid search, reranking
- **Agent improvements:** multi-agent orchestration, more tools, planning, long-running tasks
- **Production infrastructure:** CI/CD, automated testing, cloud deployment, observability
- **Additional capabilities:** voice interaction, image understanding, web search, code execution

---

## Author

**Navin Kumar**
B.Tech, Computer Science and Engineering — IIIT Bhagalpur
GitHub: [Navin-35](https://github.com/Navin-35)

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.