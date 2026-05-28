"use client";

import React, { useEffect, useRef } from "react";

// ── Types ──────────────────────────────────────────────────────
export interface LogEntry {
  id: string;
  timestamp: string;
  agent: string;
  message: string;
  eventType: string;
}

interface AgentLogProps {
  entries: LogEntry[];
  onClear: () => void;
}

// ── Agent → CSS tag class map ───────────────────────────────────
function getAgentTagClass(agent: string): string {
  const a = agent.toLowerCase();
  if (a.includes("planner"))      return "log-agent-tag tag-planner";
  if (a.includes("security"))     return "log-agent-tag tag-security";
  if (a.includes("web") || a.includes("nav")) return "log-agent-tag tag-webnav";
  if (a.includes("decision"))     return "log-agent-tag tag-decision";
  if (a.includes("payment"))      return "log-agent-tag tag-payment";
  return "log-agent-tag tag-orchestrator";
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return "--:--:--";
  }
}

// ── Log Entry Row ───────────────────────────────────────────────
function LogRow({ entry }: { entry: LogEntry }) {
  const isPhase = entry.eventType === "phase" || entry.eventType === "start";

  return (
    <div className={`log-entry${isPhase ? " phase" : ""}`}>
      <span className="log-time">{formatTime(entry.timestamp)}</span>
      <span className={getAgentTagClass(entry.agent)}>
        {entry.agent.replace(" Agent", "").toUpperCase()}
      </span>
      <span className="log-message">{entry.message}</span>
    </div>
  );
}

// ── Agent Log Panel ─────────────────────────────────────────────
export default function AgentLog({ entries, onClear }: AgentLogProps) {
  const bodyRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new entries
  useEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [entries]);

  return (
    <div className="log-panel" role="log" aria-label="Agent activity log" aria-live="polite">
      {/* Header */}
      <div className="log-header">
        <div className="log-header-left">
          <div className="log-dots" aria-hidden="true">
            <span className="log-dot log-dot-red" />
            <span className="log-dot log-dot-yellow" />
            <span className="log-dot log-dot-green" />
          </div>
          <span className="log-title">
            agent-swarm.log — {entries.length} event{entries.length !== 1 ? "s" : ""}
          </span>
        </div>
        <button
          className="log-clear-btn"
          onClick={onClear}
          aria-label="Clear log"
          disabled={entries.length === 0}
        >
          Clear
        </button>
      </div>

      {/* Body */}
      <div className="log-body" ref={bodyRef}>
        {entries.length === 0 ? (
          <div className="log-empty" aria-label="No log entries yet">
            <span className="log-empty-icon">🤖</span>
            <span className="log-empty-text">
              Submit a task to watch the agents work in real-time…
            </span>
          </div>
        ) : (
          entries.map((entry) => <LogRow key={entry.id} entry={entry} />)
        )}
      </div>
    </div>
  );
}
