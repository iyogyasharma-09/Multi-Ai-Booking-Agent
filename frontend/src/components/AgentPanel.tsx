"use client";

import React from "react";

// ── Types ──────────────────────────────────────────────────────
export type AgentStatus = "idle" | "thinking" | "done" | "error" | "waiting";

export interface AgentInfo {
  id: string;
  name: string;
  icon: string;
  description: string;
  status: AgentStatus;
}

interface AgentPanelProps {
  agents: AgentInfo[];
}

// ── Status label map ────────────────────────────────────────────
const STATUS_LABELS: Record<AgentStatus, string> = {
  idle: "Standby",
  thinking: "Active",
  done: "Done",
  error: "Error",
  waiting: "Waiting",
};

// ── Individual Agent Card ───────────────────────────────────────
function AgentCard({ agent }: { agent: AgentInfo }) {
  const cardClass = [
    "agent-card",
    agent.status !== "idle" ? agent.status : "",
  ]
    .filter(Boolean)
    .join(" ");

  const badgeClass = `agent-status-badge status-${agent.status}`;

  const statusDot =
    agent.status === "thinking" ? (
      <span className="btn-spinner" style={{ width: 6, height: 6, borderWidth: 1.5 }} />
    ) : agent.status === "done" ? (
      "✓"
    ) : agent.status === "error" ? (
      "✕"
    ) : agent.status === "waiting" ? (
      "⏸"
    ) : null;

  return (
    <div className={cardClass} role="status" aria-label={`${agent.name}: ${STATUS_LABELS[agent.status]}`}>
      <span className="agent-icon" aria-hidden="true">
        {agent.icon}
      </span>
      <span className="agent-name">{agent.name}</span>
      <span className={badgeClass}>
        {statusDot && <span>{statusDot}</span>}
        {STATUS_LABELS[agent.status]}
      </span>
    </div>
  );
}

// ── Agent Pipeline Panel ────────────────────────────────────────
export default function AgentPanel({ agents }: AgentPanelProps) {
  const activeCount = agents.filter((a) => a.status === "thinking").length;
  const doneCount   = agents.filter((a) => a.status === "done").length;

  return (
    <div>
      {/* Progress bar */}
      {doneCount > 0 && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
            marginBottom: "0.85rem",
          }}
        >
          <div
            style={{
              flex: 1,
              height: 4,
              background: "rgba(99,102,241,0.12)",
              borderRadius: 9999,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${(doneCount / agents.length) * 100}%`,
                background: "linear-gradient(90deg, #6366f1, #06b6d4)",
                borderRadius: 9999,
                transition: "width 0.6s cubic-bezier(0.4,0,0.2,1)",
              }}
            />
          </div>
          <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", whiteSpace: "nowrap" }}>
            {doneCount}/{agents.length} agents completed
          </span>
        </div>
      )}

      {/* Agent cards grid */}
      <div className="agent-grid">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>

      {/* Active agent label */}
      {activeCount > 0 && (
        <div
          style={{
            textAlign: "center",
            fontSize: "0.78rem",
            color: "var(--text-accent)",
            fontWeight: 600,
            marginTop: "0.5rem",
            animation: "pulse 2s ease-in-out infinite",
          }}
        >
          ⚡ {agents.find((a) => a.status === "thinking")?.name} is working…
        </div>
      )}
    </div>
  );
}
