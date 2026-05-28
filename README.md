# 🐝 TaskHive — Secure Multi-Agent AI Task Automation

> **AI swarm for secure autonomous web task execution.**  
> Five specialized AI agents collaborate to safely book tickets, pay bills, and complete real-world web tasks — with a built-in security trust layer and human-in-the-loop approval.

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────┐
│        Orchestrator Agent       │  ← Google Antigravity SDK
│  (Planner + Task Coordinator)   │
└────────────┬────────────────────┘
             │  coordinates
    ┌─────────┼──────────┬──────────────┐
    ▼         ▼          ▼              ▼
┌───────┐ ┌──────┐ ┌──────────┐ ┌──────────┐
│Planner│ │ Web  │ │Security  │ │Decision  │
│ Agent │ │ Nav  │ │  Agent   │ │  Agent   │
└───────┘ └──────┘ └──────────┘ └──────────┘
                                       │
                                 ┌──────────┐
                                 │ Payment  │
                                 │  Agent   │
                                 │(Simulated│
                                 └──────────┘
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A **Gemini API key** from [Google AI Studio](https://aistudio.google.com/app/api-keys)

### 1. Set up environment
```bash
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the backend
```bash
uvicorn api.server:app --reload --port 8000
```

### 4. Start the frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```

### 5. Open the dashboard
Visit **http://localhost:3000** and submit a task like:
> "Book 2 tickets for Mission Impossible on Sunday evening under ₹800"

---

## 🤖 The Five Agents

| Agent | Role | Key Tools |
|-------|------|-----------|
| 🧠 **Planner** | Decomposes natural language into structured plans | `parse_user_intent`, `create_task_plan` |
| 🔒 **Security** | Multi-layer URL/domain trust validation | `check_url_safety`, `check_domain_reputation`, `verify_payment_page` |
| 🌐 **Web Nav** | Simulates browser navigation & data extraction | `search_booking_websites`, `extract_movie_listings`, `navigate_to_seat_selection` |
| ✅ **Decision** | Validates selections against user constraints | `calculate_total_amount`, `check_budget_constraint` |
| 💳 **Payment** | Safe simulated payment flow (stops before OTP) | `simulate_payment`, `generate_booking_reference` |

---

## 🔒 Security Features (The Key Innovation)

The **Security Agent** performs:
- ✅ HTTPS/SSL verification
- ✅ Domain typosquatting detection (paypa1, amaz0n, etc.)
- ✅ Phishing URL pattern matching
- ✅ Domain reputation & age scoring
- ✅ Fake payment page detection
- ✅ Page content threat scanning

**Trust Score**: 0–100. Only scores ≥ 60 proceed. Shown as an animated ring in the UI.

---

## 💻 Demo Mode

The frontend includes a **built-in demo mode** — if the Python backend is not running, clicking "Launch Swarm" simulates the full agent pipeline locally with realistic events, timings, and the human approval modal.

---

## 📁 Project Structure

```
Multi-Agent System/
├── agents/
│   ├── orchestrator.py      # Master coordinator
│   ├── planner_agent.py     # Task decomposition
│   ├── security_agent.py    # Trust validation
│   ├── web_nav_agent.py     # Web navigation
│   ├── decision_agent.py    # Constraint validation
│   └── payment_agent.py     # Simulated payment
├── tools/
│   ├── security_tools.py    # URL/domain safety tools
│   ├── web_tools.py         # Browser simulation tools
│   ├── task_tools.py        # Planning/parsing tools
│   └── payment_tools.py     # Payment simulation tools
├── api/
│   └── server.py            # FastAPI + WebSocket server
├── frontend/                # Next.js 14 dashboard
│   └── src/
│       ├── app/page.tsx     # Main dashboard
│       └── components/      # AgentPanel, AgentLog, SecurityBadge, ApprovalModal
├── requirements.txt
└── .env.example
```

---

## 🎯 Hackathon Keywords

- **Multi-agent orchestration** via Google Antigravity SDK
- **Autonomous workflow execution** with security validation
- **AI trust layer** — URL safety scoring before any web interaction
- **Human-in-the-loop approval** before payment
- **Agent collaboration** — 5 specialized agents, one pipeline
- **Secure web automation** — demo-safe, stops before OTP

---

## 🚀 Running Individual Agents (CLI)

```bash
# Run the full orchestrator pipeline
python agents/orchestrator.py

# Test individual agents
python agents/security_agent.py
python agents/planner_agent.py
python agents/payment_agent.py
```

---

## ⚠️ Important Notes

- **No real payments**: The Payment Agent is purely simulated. No real money is moved.
- **No live web scraping**: Web navigation uses realistic mock data for stable demos.
- **API key required**: Set `GEMINI_API_KEY` in `.env` to use real agents.
- **Demo mode**: The frontend works without the backend for presentation purposes.

---

*Built with ❤️ using Google Antigravity SDK, FastAPI, and Next.js*
