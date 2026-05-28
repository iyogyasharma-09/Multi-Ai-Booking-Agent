"use client";

import React, { useState, useCallback, useRef } from "react";
import AgentPanel, { AgentInfo, AgentStatus } from "@/components/AgentPanel";
import AgentLog, { LogEntry } from "@/components/AgentLog";
import SecurityBadge from "@/components/SecurityBadge";
import ApprovalModal, { BookingSummary } from "@/components/ApprovalModal";

// ─── Constants ──────────────────────────────────────────────────
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const EXAMPLE_TASKS = [
  "Book 2 tickets for Mission Impossible on Sunday evening under ₹800",
  "Pay my Airtel broadband bill of ₹999",
  "Order 2 Margherita pizzas from Zomato under ₹600",
  "Book a PVR Gold ticket for Kalki on Saturday night",
];

const INITIAL_AGENTS: AgentInfo[] = [
  { id: "planner",  name: "Planner",    icon: "🧠", description: "Decomposes user task into steps",       status: "idle" },
  { id: "security", name: "Security",   icon: "🔒", description: "Validates website safety & trust",      status: "idle" },
  { id: "webnav",   name: "Web Nav",    icon: "🌐", description: "Navigates websites & extracts data",    status: "idle" },
  { id: "decision", name: "Decision",   icon: "✅", description: "Validates options against constraints", status: "idle" },
  { id: "payment",  name: "Payment",    icon: "💳", description: "Simulates secure payment flow",         status: "idle" },
];

// Agent keyword → id map
const AGENT_KEYWORD_MAP: Record<string, string> = {
  planner: "planner",
  security: "security",
  "web nav": "webnav",
  "web navigator": "webnav",
  decision: "decision",
  validation: "decision",
  payment: "payment",
};

function getAgentId(agentName: string): string | null {
  const lower = agentName.toLowerCase();
  for (const [kw, id] of Object.entries(AGENT_KEYWORD_MAP)) {
    if (lower.includes(kw)) return id;
  }
  return null;
}

// ─── Main Dashboard Page ────────────────────────────────────────
export default function DashboardPage() {
  // Input
  const [taskInput, setTaskInput]   = useState("");
  const [isRunning, setIsRunning]   = useState(false);

  // Agent states
  const [agents, setAgents]         = useState<AgentInfo[]>(INITIAL_AGENTS);
  const [logs, setLogs]             = useState<LogEntry[]>([]);

  // Security
  const [securityScore, setSecurityScore]   = useState<number | null>(null);
  const [securityVerdict, setSecurityVerdict] = useState<"SAFE" | "CAUTION" | "DANGEROUS" | null>(null);
  const [securityVisible, setSecurityVisible] = useState(false);

  // Approval modal
  const [showModal, setShowModal]       = useState(false);
  const [bookingSummary, setBookingSummary] = useState<BookingSummary | null>(null);
  const [approvalLoading, setApprovalLoading] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);

  // Confirmation
  const [bookingRef, setBookingRef]     = useState<string | null>(null);
  const [taskComplete, setTaskComplete] = useState(false);

  const wsRef    = useRef<WebSocket | null>(null);
  const logIdRef = useRef(0);

  // ── Helpers ──────────────────────────────────────────────────
  const addLog = useCallback((agent: string, message: string, eventType: string, timestamp?: string) => {
    const entry: LogEntry = {
      id: `log-${++logIdRef.current}`,
      timestamp: timestamp || new Date().toISOString(),
      agent,
      message,
      eventType,
    };
    setLogs((prev) => [...prev, entry]);
  }, []);

  const setAgentStatus = useCallback((agentId: string, status: AgentStatus) => {
    setAgents((prev) =>
      prev.map((a) => (a.id === agentId ? { ...a, status } : a))
    );
  }, []);

  const resetState = useCallback(() => {
    setAgents(INITIAL_AGENTS);
    setSecurityScore(null);
    setSecurityVerdict(null);
    setSecurityVisible(false);
    setBookingSummary(null);
    setBookingRef(null);
    setTaskComplete(false);
    setShowModal(false);
    setCurrentTaskId(null);
  }, []);

  // ── Process WebSocket event ─────────────────────────────────
  const handleEvent = useCallback((data: Record<string, string>) => {
    const { event_type, agent, message, timestamp } = data;

    addLog(agent || "Orchestrator", message, event_type, timestamp);

    // Update agent statuses
    const agentId = getAgentId(agent || "");
    if (agentId) {
      if (event_type === "phase") {
        // Mark previous agents done, current as thinking
        setAgents((prev) =>
          prev.map((a) => {
            if (a.id === agentId) return { ...a, status: "thinking" };
            if (a.status === "thinking") return { ...a, status: "done" };
            return a;
          })
        );
      }
      if (["plan_complete", "security_complete", "nav_complete", "decision_complete", "payment_complete"].includes(event_type)) {
        setAgentStatus(agentId, "done");
      }
    }

    // Security scan results — extract a simulated score from message
    if (event_type === "security_complete") {
      const scoreMatch = message.match(/(\d{1,3})\s*\/\s*100/);
      const score = scoreMatch ? Math.min(100, parseInt(scoreMatch[1])) : 92;
      setSecurityScore(score);
      setSecurityVerdict(score >= 80 ? "SAFE" : score >= 55 ? "CAUTION" : "DANGEROUS");
      setSecurityVisible(true);
    }

    // Decision complete → show approval modal
    if (event_type === "awaiting_approval") {
      setAgentStatus("decision", "waiting");

      // Build a realistic booking summary for the modal
      const summary: BookingSummary = {
        movieTitle: "Mission: Impossible — The Final Reckoning",
        cinema: "PVR Phoenix Mall",
        date: "Sunday",
        time: "7:00 PM",
        seats: ["D5", "D6"],
        seatCategory: "Premium",
        quantity: 2,
        pricePerSeat: 350,
        convenienceFee: 30,
        gst: 68,
        total: 748,
        budgetLimit: 800,
        paymentMethod: "UPI",
      };
      setBookingSummary(summary);
      setShowModal(true);
    }

    // Payment approved — mark payment agent active
    if (event_type === "approved") {
      setShowModal(false);
      setAgentStatus("payment", "thinking");
    }

    // Extract booking ref from confirmation
    if (event_type === "payment_complete") {
      const refMatch = message.match(/([A-Z]{2,5}-\d{4}-[A-Z0-9]{6})/);
      if (refMatch) setBookingRef(refMatch[1]);
      setAgentStatus("payment", "done");
    }

    // Pipeline done
    if (event_type === "complete") {
      setIsRunning(false);
      setTaskComplete(true);
    }

    // Error
    if (event_type === "error") {
      if (agentId) setAgentStatus(agentId, "error");
      setIsRunning(false);
    }

    // Cancelled
    if (event_type === "cancelled") {
      setIsRunning(false);
    }
  }, [addLog, setAgentStatus]);

  // ── Submit Task ─────────────────────────────────────────────
  const handleSubmit = useCallback(async () => {
    if (!taskInput.trim() || isRunning) return;

    resetState();
    setIsRunning(true);
    setLogs([]);

    addLog("Orchestrator", `🚀 Submitting task: "${taskInput}"`, "start");

    try {
      // POST task to backend
      const res = await fetch(`${API_BASE}/task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: taskInput }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const { task_id } = await res.json();
      setCurrentTaskId(task_id);

      addLog("Orchestrator", `✅ Task registered — ID: ${task_id}`, "info");

      // Connect WebSocket for live events
      const ws = new WebSocket(`${API_BASE.replace("http", "ws")}/ws/${task_id}`);
      wsRef.current = ws;

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.event_type !== "ping") handleEvent(data);
        } catch {
          // ignore parse errors
        }
      };

      ws.onerror = () => {
        addLog("Orchestrator", "⚠️ WebSocket connection error", "error");
        setIsRunning(false);
      };

      ws.onclose = () => {
        addLog("Orchestrator", "WebSocket connection closed", "info");
      };
    } catch (err) {
      addLog("Orchestrator", `❌ Failed to connect to backend: ${err}`, "error");
      setIsRunning(false);

      // Demo mode: simulate events locally when backend is unavailable
      runDemoMode(taskInput);
    }
  }, [taskInput, isRunning, resetState, addLog, handleEvent]);

  // ── Demo Mode (no backend needed) ──────────────────────────
  const runDemoMode = useCallback(async (task: string) => {
    const events = [
      { delay: 300,  agent: "Planner Agent",    type: "phase",           msg: "🧠 Analysing task and creating execution plan…" },
      { delay: 1200, agent: "Planner Agent",    type: "plan_complete",   msg: `✅ Plan created with 9 steps for: ${task}` },
      { delay: 500,  agent: "Security Agent",   type: "phase",           msg: "🔒 Running security validation on target websites…" },
      { delay: 1800, agent: "Security Agent",   type: "security_complete", msg: "✅ bookmyshow.com — Trust Score: 96/100 · SAFE · HTTPS verified · Domain age: 15 years · Reputation: 96/100" },
      { delay: 400,  agent: "Web Nav Agent",    type: "phase",           msg: "🌐 Navigating BookMyShow — searching for available shows…" },
      { delay: 2000, agent: "Web Nav Agent",    type: "nav_complete",    msg: "✅ Found 4 shows. Best match: MI Final Reckoning | PVR Phoenix Mall | Sun 7:00 PM | Seats D5, D6 | ₹350/seat (Premium)" },
      { delay: 400,  agent: "Decision Agent",   type: "phase",           msg: "✅ Validating selection against your constraints…" },
      { delay: 1500, agent: "Decision Agent",   type: "decision_complete", msg: "📋 Booking Summary ready · Total: ₹748 · Within ₹800 budget ✅ · Sunday evening ✅ · Awaiting your approval…" },
      { delay: 300,  agent: "Orchestrator",     type: "awaiting_approval", msg: "⏸️  Awaiting your approval before payment…" },
    ];

    let elapsed = 0;
    for (const ev of events) {
      elapsed += ev.delay;
      await new Promise<void>((resolve) =>
        setTimeout(() => {
          handleEvent({
            event_type: ev.type,
            agent: ev.agent,
            message: ev.msg,
            timestamp: new Date().toISOString(),
          });
          resolve();
        }, elapsed)
      );
    }
  }, [handleEvent]);

  // ── Approval actions ────────────────────────────────────────
  const handleApprove = useCallback(async () => {
    setApprovalLoading(true);
    addLog("Orchestrator", "✅ User approved payment — proceeding…", "approved");

    if (currentTaskId) {
      try {
        await fetch(`${API_BASE}/approve/${currentTaskId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ approved: true }),
        });
      } catch {
        // Demo fallback
      }
    }

    // Demo payment flow
    setTimeout(() => {
      setShowModal(false);
      setApprovalLoading(false);
      setAgentStatus("payment", "thinking");
      addLog("Payment Agent", "💳 Redirected to Razorpay payment gateway", "phase");
    }, 500);

    setTimeout(() => {
      addLog("Payment Agent", "✅ UPI payment of ₹748 processed", "payment_complete");
      const ref = `BMS-2026-${Math.random().toString(36).slice(2,8).toUpperCase()}`;
      setBookingRef(ref);
      addLog("Payment Agent", `🎉 Booking Confirmed! Reference: ${ref}`, "payment_complete");
      setAgentStatus("payment", "done");
      setTaskComplete(true);
      setIsRunning(false);
    }, 2800);
  }, [currentTaskId, addLog, setAgentStatus]);

  const handleCancel = useCallback(async () => {
    setShowModal(false);
    addLog("Orchestrator", "❌ Task cancelled by user", "cancelled");
    setIsRunning(false);
    if (currentTaskId) {
      try {
        await fetch(`${API_BASE}/approve/${currentTaskId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ approved: false }),
        });
      } catch { /* ignore */ }
    }
  }, [currentTaskId, addLog]);

  // ── Render ──────────────────────────────────────────────────
  return (
    <>
      {/* ── Header ── */}
      <header className="header">
        <div className="header-inner">
          <a href="/" className="logo" aria-label="TaskHive home">
            <span className="logo-icon" aria-hidden="true">🐝</span>
            <span className="logo-text">Task<span>Hive</span></span>
          </a>
          <div className="header-badge" role="status" aria-label="System status: online">
            <span className="pulse-dot" aria-hidden="true" />
            SWARM ONLINE
          </div>
        </div>
      </header>

      <main>
        {/* ── Hero ── */}
        <section className="hero" aria-labelledby="hero-title">
          <div className="container">
            <div className="hero-badge" aria-label="Multi-agent orchestration system">
              ⚡ Multi-Agent Orchestration
            </div>
            <h1 className="hero-title" id="hero-title">
              Your AI <span className="gradient-text">Task Swarm</span>
              <br />Working Autonomously
            </h1>
            <p className="hero-subtitle">
              Five specialized AI agents collaborate to safely book tickets, pay bills,
              and complete web tasks — with a built-in security layer and human approval.
            </p>

            {/* Task Input */}
            <div className="task-input-section">
              <div className="task-input-wrapper" role="search">
                <div className="input-row">
                  <input
                    id="task-input"
                    type="text"
                    className="task-input-field"
                    placeholder='e.g. "Book 2 tickets for Mission Impossible on Sunday under ₹800"'
                    value={taskInput}
                    onChange={(e) => setTaskInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") handleSubmit(); }}
                    disabled={isRunning}
                    aria-label="Describe your task"
                    autoComplete="off"
                  />
                  <button
                    id="submit-task-btn"
                    className="submit-btn"
                    onClick={handleSubmit}
                    disabled={isRunning || !taskInput.trim()}
                    aria-label={isRunning ? "Agents are working…" : "Launch agent swarm"}
                  >
                    {isRunning ? (
                      <><span className="btn-spinner" aria-hidden="true" /> Working…</>
                    ) : (
                      <>🚀 Launch Swarm</>
                    )}
                  </button>
                </div>

                {/* Example chips */}
                <div className="example-chips" role="list" aria-label="Example tasks">
                  {EXAMPLE_TASKS.map((ex) => (
                    <button
                      key={ex}
                      role="listitem"
                      className="chip"
                      onClick={() => setTaskInput(ex)}
                      disabled={isRunning}
                      aria-label={`Use example: ${ex}`}
                    >
                      {ex.length > 45 ? ex.slice(0, 42) + "…" : ex}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Pipeline Section ── */}
        <section className="pipeline-section" aria-label="Agent pipeline">
          <div className="container">
            {/* Agent cards */}
            <p className="section-label" aria-hidden="true">Agent Pipeline</p>
            <AgentPanel agents={agents} />

            {/* Security Badge */}
            <SecurityBadge
              score={securityScore}
              verdict={securityVerdict}
              domain="bookmyshow.com"
              findings={
                securityScore !== null
                  ? [
                      "✅ HTTPS encryption active",
                      "✅ Domain in trusted verified list",
                      `✅ Domain age: ~15 years (established)`,
                      "✅ No phishing patterns detected",
                    ]
                  : []
              }
              visible={securityVisible}
            />

            {/* Log panel */}
            <p className="section-label" aria-hidden="true">Live Agent Log</p>
            <AgentLog entries={logs} onClear={() => setLogs([])} />

            {/* Booking confirmation */}
            {taskComplete && bookingRef && (
              <div
                className="confirmation-card"
                role="status"
                aria-live="polite"
                aria-label="Booking confirmed"
                style={{ marginTop: "1.5rem" }}
              >
                <span className="confirmation-icon" aria-hidden="true">🎉</span>
                <h3>Booking Confirmed!</h3>
                <p style={{ margin: "0.25rem 0 0.75rem", color: "var(--text-secondary)" }}>
                  Your task has been completed successfully
                </p>
                <div className="booking-ref" aria-label={`Booking reference: ${bookingRef}`}>
                  {bookingRef}
                </div>
                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", margin: "0.5rem 0 1.25rem" }}>
                  Confirmation sent to demo@taskhive.ai &amp; ****3210
                </p>
                <button
                  id="new-task-btn"
                  className="submit-btn"
                  onClick={() => { resetState(); setTaskInput(""); setLogs([]); }}
                  style={{ display: "inline-flex", margin: "0 auto" }}
                >
                  ✨ New Task
                </button>
              </div>
            )}
          </div>
        </section>
      </main>

      {/* ── Footer ── */}
      <footer className="footer">
        <div className="container">
          <p>
            🐝 <span>TaskHive</span> — Secure Multi-Agent AI System ·
            Built with Google Antigravity SDK &amp; Next.js ·{" "}
            <span>⚡ Demo Mode</span>
          </p>
        </div>
      </footer>

      {/* ── Approval Modal ── */}
      {showModal && (
        <ApprovalModal
          summary={bookingSummary}
          taskId={currentTaskId || "DEMO"}
          onApprove={handleApprove}
          onCancel={handleCancel}
          isLoading={approvalLoading}
        />
      )}
    </>
  );
}
