"use client";

import React, { useEffect, useRef, useState } from "react";

// ── Types ──────────────────────────────────────────────────────
interface SecurityBadgeProps {
  score: number | null;      // 0–100, null = not yet checked
  verdict: "SAFE" | "CAUTION" | "DANGEROUS" | null;
  domain?: string;
  findings?: string[];
  visible: boolean;
}

// ── Helpers ─────────────────────────────────────────────────────
const CIRCUMFERENCE = 2 * Math.PI * 36; // radius = 36

function scoreToColor(score: number): string {
  if (score >= 80) return "#10b981"; // green
  if (score >= 55) return "#f59e0b"; // amber
  return "#ef4444";                   // red
}

function scoreToOffset(score: number): number {
  return CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
}

function verdictClass(verdict: string | null): string {
  if (verdict === "SAFE")      return "verdict-safe";
  if (verdict === "CAUTION")   return "verdict-caution";
  if (verdict === "DANGEROUS") return "verdict-danger";
  return "";
}

// ── Security Badge ──────────────────────────────────────────────
export default function SecurityBadge({
  score,
  verdict,
  domain,
  findings,
  visible,
}: SecurityBadgeProps) {
  const [displayScore, setDisplayScore] = useState(0);
  const animRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Animate score counter
  useEffect(() => {
    if (score === null) { setDisplayScore(0); return; }

    let current = 0;
    const target = score;
    const duration = 1200;
    const steps = 60;
    const increment = target / steps;
    const interval = duration / steps;

    const tick = () => {
      current = Math.min(current + increment, target);
      setDisplayScore(Math.round(current));
      if (current < target) {
        animRef.current = setTimeout(tick, interval);
      }
    };
    tick();

    return () => { if (animRef.current) clearTimeout(animRef.current); };
  }, [score]);

  if (!visible) return null;

  const strokeColor = score !== null ? scoreToColor(score) : "rgba(99,102,241,0.3)";
  const offset = score !== null ? scoreToOffset(score) : CIRCUMFERENCE;

  return (
    <div className={`security-panel${visible ? " visible" : ""}`} aria-label="Security analysis results">
      {/* Circular trust ring */}
      <div className="trust-ring" role="img" aria-label={`Trust score: ${displayScore} out of 100`}>
        <svg width="90" height="90" viewBox="0 0 90 90">
          <circle className="trust-ring-track" cx="45" cy="45" r="36" />
          <circle
            className="trust-ring-fill"
            cx="45" cy="45" r="36"
            stroke={strokeColor}
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
            style={{
              transition: "stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1), stroke 0.5s ease",
            }}
          />
        </svg>
        <div className="trust-ring-label">
          <span className="trust-score-num" style={{ color: strokeColor }}>
            {displayScore}
          </span>
          <span className="trust-score-sub">/100</span>
        </div>
      </div>

      {/* Info */}
      <div className="security-info">
        <h4>Security Analysis{domain ? ` — ${domain}` : ""}</h4>

        {verdict && (
          <div className={`security-verdict ${verdictClass(verdict)}`}>
            {verdict === "SAFE" ? "✅" : verdict === "CAUTION" ? "⚠️" : "🚨"}
            {verdict}
          </div>
        )}

        {findings && findings.length > 0 && (
          <ul className="security-findings" aria-label="Security findings">
            {findings.slice(0, 4).map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
