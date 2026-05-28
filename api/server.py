"""
TaskHive — FastAPI Backend Server
Real-time WebSocket streaming of multi-agent execution events.
"""

import asyncio
import json
import uuid
import sys
import os
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Import orchestrator
from agents.orchestrator import run_task

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="TaskHive API",
    description="Secure multi-agent AI task automation system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-Memory Task Store ─────────────────────────────────────────────────────

tasks: dict[str, dict[str, Any]] = {}
task_queues: dict[str, asyncio.Queue] = {}
approval_events: dict[str, asyncio.Event] = {}


# ─── Schemas ──────────────────────────────────────────────────────────────────

class TaskRequest(BaseModel):
    task: str
    user_name: str = "TaskHive User"
    user_email: str = "user@taskhive.ai"
    user_phone: str = "9876543210"
    payment_method: str = "UPI"


class ApprovalRequest(BaseModel):
    approved: bool


# ─── Helper: Event Emitter ────────────────────────────────────────────────────

def build_event(
    event_type: str,
    agent: str,
    message: str,
    task_id: str,
    extra: dict | None = None,
) -> dict:
    return {
        "task_id": task_id,
        "event_type": event_type,
        "agent": agent,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        **(extra or {}),
    }


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "TaskHive API", "version": "1.0.0"}


@app.post("/task")
async def create_task(req: TaskRequest):
    """Submit a new task to the agent swarm."""
    task_id = str(uuid.uuid4())[:8].upper()

    tasks[task_id] = {
        "id": task_id,
        "task": req.task,
        "user_name": req.user_name,
        "user_email": req.user_email,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "events": [],
        "results": {},
    }
    task_queues[task_id] = asyncio.Queue()
    approval_events[task_id] = asyncio.Event()

    # Start the agent pipeline in background
    asyncio.create_task(_run_pipeline(task_id, req))

    return {"task_id": task_id, "status": "started", "message": f"Task {task_id} submitted"}


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the current status of a task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.post("/approve/{task_id}")
async def approve_task(task_id: str, req: ApprovalRequest):
    """Human-in-the-loop approval endpoint. Called from the frontend modal."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_id not in approval_events:
        raise HTTPException(status_code=400, detail="No pending approval for this task")

    tasks[task_id]["approved"] = req.approved
    approval_events[task_id].set()  # Signal the waiting coroutine

    if req.approved:
        return {"message": "Payment approved. Processing..."}
    else:
        tasks[task_id]["status"] = "cancelled"
        return {"message": "Task cancelled by user."}


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time agent event streaming."""
    await websocket.accept()

    if task_id not in tasks:
        await websocket.send_json({"error": "Task not found"})
        await websocket.close()
        return

    queue = task_queues.get(task_id)
    if not queue:
        await websocket.send_json({"error": "No event queue for task"})
        await websocket.close()
        return

    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=120.0)
                await websocket.send_json(event)

                # If pipeline is complete, close connection
                if event.get("event_type") in ("complete", "error", "cancelled"):
                    break

            except asyncio.TimeoutError:
                await websocket.send_json({"event_type": "ping", "message": "alive"})

    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()


# ─── Pipeline Runner ──────────────────────────────────────────────────────────

async def _run_pipeline(task_id: str, req: TaskRequest):
    """Background task runner — orchestrates agents and streams events."""
    queue = task_queues[task_id]
    tasks[task_id]["status"] = "running"

    async def emit(event_type: str, agent: str, message: str, **extra):
        event = build_event(event_type, agent, message, task_id, extra or None)
        tasks[task_id]["events"].append(event)
        await queue.put(event)

    try:
        # Custom callback for orchestrator
        async def agent_callback(event_type: str, agent: str, message: str):
            await emit(event_type, agent, message)

            # When decision is complete, pause for user approval
            if event_type == "decision_complete":
                tasks[task_id]["status"] = "awaiting_approval"
                await emit("awaiting_approval", "Orchestrator",
                           "⏸️  Awaiting your approval before payment...")

                # Wait for approval (timeout: 5 minutes)
                approval_event = approval_events.get(task_id)
                if approval_event:
                    try:
                        await asyncio.wait_for(approval_event.wait(), timeout=300.0)
                    except asyncio.TimeoutError:
                        tasks[task_id]["status"] = "timeout"
                        await emit("error", "Orchestrator",
                                   "⏰ Approval timed out after 5 minutes.")
                        return

                    if not tasks[task_id].get("approved", False):
                        tasks[task_id]["status"] = "cancelled"
                        await emit("cancelled", "Orchestrator",
                                   "❌ Task cancelled by user.")
                        return

                tasks[task_id]["status"] = "running"
                await emit("approved", "Orchestrator", "✅ User approved! Proceeding to payment...")

        # Run the full pipeline
        results = await run_task(
            user_task=req.task,
            auto_approve=False,
            event_callback=agent_callback,
        )

        tasks[task_id]["results"] = results
        tasks[task_id]["status"] = "completed"

    except Exception as e:
        err_msg = str(e)
        # Provide a user-friendly message for known error types
        if "429" in err_msg or "Too Many Requests" in err_msg:
            friendly = "⚠️ AI model is busy (rate limit). Please wait 60s and try again, or try a different task."
        else:
            friendly = f"❌ Pipeline error: {err_msg[:200]}"
        tasks[task_id]["status"] = "error"
        await emit("error", "Orchestrator", friendly)
        # Do NOT re-raise — let the WebSocket close cleanly
    finally:
        # Always signal pipeline end so WebSocket loop exits
        await queue.put(build_event("complete", "Orchestrator", "Pipeline finished.", task_id))
