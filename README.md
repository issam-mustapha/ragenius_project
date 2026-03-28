# 🧠 RAGenius — Intelligent AI Agent with RAG, FAISS & Multi-Memory

> **Personalized. Secure. Context-aware.** A production-grade AI chatbot that understands your documents, remembers your preferences, and keeps your data private.

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat)](https://langchain.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ What is RAGenius?

RAGenius is a full-stack AI chatbot platform that combines **Retrieval-Augmented Generation (RAG)**, **FAISS vector search**, and a **dual-memory architecture** to deliver accurate, personalized, and secure answers from your own documents.

Unlike generic chatbots, RAGenius:
- 📄 **Reads your PDFs & images** — upload documents and query them instantly
- 🧠 **Remembers you** — long-term memory stores your preferences, profession, and communication style
- 🔒 **Protects your data** — PII detection masks sensitive info before it ever reaches the LLM
- 🏠 **Runs locally** — powered by Mistral 7B via Ollama, fully offline-capable

---

## 🚀 Key Features

### For Authenticated Users
| Feature | Description |
|---|---|
| 📂 Document Upload | Upload PDFs & images; queries are answered from your files |
| 🔍 Smart Search | FAISS similarity search across all your uploaded documents |
| 🧬 Long-Term Memory | Your preferences, hobbies, language & style are remembered |
| 💬 Conversation History | Access and continue all past conversations |
| 🖼️ OCR Support | Extract and query text from images and scanned docs |
| 🔐 Secure Auth | Token-based auth with Google OAuth and form login |

### For All Users
| Feature | Description |
|---|---|
| ⚡ Short-Term Memory | Session-scoped context for every conversation |
| 🛡️ PII Masking | Sensitive data stripped before reaching the LLM |
| ✅ Response Validation | Middleware validates every response before delivery |
| 🌐 Modern UI | Clean, responsive interface built with Next.js & Tailwind |

---

## 🏗️ Architecture Overview

```
User Query
    │
    ▼
┌───────────────────────────────────────────┐
│              Middleware Layer             │
│   PII Detection → Query Sanitization     │
└────────────────────┬──────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────┐
│           Central AI Agent               │
│  (LangGraph orchestration engine)        │
│                                           │
│  ┌─────────┐  ┌────────┐  ┌───────────┐  │
│  │   RAG   │  │  LLM   │  │  Memory   │  │
│  │  FAISS  │  │Mistral │  │Short+Long │  │
│  └─────────┘  └────────┘  └───────────┘  │
└────────────────────┬──────────────────────┘
                     │
                     ▼
           Response Validation
                     │
                     ▼
              User Interface
```

### Data Flow by Input Type
- **PDF** → Chunking → Embeddings → FAISS (per-user isolated index)
- **Image** → OCR → Text Cleaning → LLM Context
- **Direct Question** → Short-term memory + LLM → Response
- **Document Query** → FAISS similarity search → RAG → LLM → Response

---

## 🛠️ Tech Stack

### Backend
| Technology | Role |
|---|---|
| **LangChain** | AI agent framework — reasoning, tools, memory |
| **LangGraph** | Stateful multi-step agent orchestration |
| **FastAPI** | High-performance REST API |
| **Mistral 7B** | Local LLM via Ollama |
| **FAISS** | Vector store for semantic document search |
| **PostgreSQL** | Long-term memory & user metadata |
| **OCR** | Image-to-text for scanned documents |

### Frontend
| Technology | Role |
|---|---|
| **Next.js** | React framework with SSR/SSG |
| **TypeScript** | Type-safe frontend development |
| **Tailwind CSS** | Utility-first responsive UI |
| **Axios** | HTTP client for API communication |

### DevOps & Tools
`Docker` · `Git/GitHub` · `VS Code` · `Postman`

---

## 📸 Screenshots

### Chat Interface — Non-Authenticated User

> *Non-authenticated users interact using short-term memory. All context is cleared on session end.*

![Non-authenticated chat](assets/images/non_auth.png)

### Chat Interface — Authenticated User

> *Full access: PDF upload, conversation history, long-term personalization.*

![Authenticated chat](assets/images/auth_user_1.png)

### Conversation Continuation

> *Users can resume past conversations and manage multiple chat threads.*

![Conversation continuation](assets/images/auth_user_2.png)

### Authentication — Sign In

> *Secure login via email/password or Google OAuth.*

![Sign in page](assets/images/login.png)

### Authentication — Sign Up

> *Create an account with form or Google to unlock all features.*

![Sign up page](assets/images/sign_up.png)

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- [Ollama](https://ollama.ai) with Mistral 7B pulled

```bash
# Pull Mistral 7B locally
ollama pull mistral
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/issam-mustapha/ragenius_project.git
cd ragenius_project

# 2. Start all services with Docker
docker-compose up --build

# Frontend
cd frontend
npm install
npm run dev
```

### Environment Variables

Create a `.env` file in `/backend`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ragenius
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 🔒 Security Features

- ✅ Token-based JWT authentication
- ✅ Google OAuth 2.0 support
- ✅ PII detection middleware (masks sensitive data pre-LLM)
- ✅ Per-user isolated FAISS indexes (no cross-user data leakage)
- ✅ Response validation before delivery to client

---

## 🗺️ Use Case Diagram

![Use Case Diagram](assets/images/use_case.png)

---

## 📖 Documentation
| Resource | Link |
|---|---|
| API Reference | `/docs` (FastAPI auto-docs when running) |
| Full Project Report | `report/RAGenius_Report.pdf` |

## 🗺️ Architecture Diagram

![Architecture Workflow](assets/images/work_flow.png)

---

## 👤 Author

**Issam Adoch**
- 🐙 GitHub: [@issam-mustapha](https://github.com/issam-mustapha)
- 💼 LinkedIn: [issam-ai-engineer](https://www.linkedin.com/in/issam-ai-engineer)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## ⭐ If this project helped you, please give it a star!

*Built with ❤️ using LangChain, LangGraph, FAISS, and a modular LLM backend —  
works with Mistral 7B (local via Ollama), GPT-4, Claude, Gemini, or any LangChain-compatible model.*
