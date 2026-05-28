"use client";

import React from "react";

// ── Types ──────────────────────────────────────────────────────
export interface BookingSummary {
  movieTitle: string;
  cinema: string;
  date: string;
  time: string;
  seats: string[];
  seatCategory: string;
  quantity: number;
  pricePerSeat: number;
  convenienceFee: number;
  gst: number;
  total: number;
  budgetLimit: number;
  paymentMethod: string;
}

interface ApprovalModalProps {
  summary: BookingSummary | null;
  taskId: string;
  onApprove: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

// ── Approval Modal ──────────────────────────────────────────────
export default function ApprovalModal({
  summary,
  taskId,
  onApprove,
  onCancel,
  isLoading = false,
}: ApprovalModalProps) {
  if (!summary) return null;

  const withinBudget = summary.total <= summary.budgetLimit;
  const savings = summary.budgetLimit - summary.total;

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onClick={(e) => { if (e.target === e.currentTarget) onCancel(); }}
    >
      <div className="modal-box">
        {/* Header */}
        <div className="modal-header">
          <span className="modal-header-icon" aria-hidden="true">📋</span>
          <div>
            <h3 id="modal-title">Booking Summary</h3>
            <p>Review details before payment · Task {taskId}</p>
          </div>
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* Details table */}
          <table className="booking-summary-table" aria-label="Booking details">
            <tbody>
              <tr>
                <td>🎬 Movie</td>
                <td>{summary.movieTitle}</td>
              </tr>
              <tr>
                <td>📍 Venue</td>
                <td>{summary.cinema}</td>
              </tr>
              <tr>
                <td>📅 Date</td>
                <td>{summary.date}</td>
              </tr>
              <tr>
                <td>🕐 Time</td>
                <td>{summary.time}</td>
              </tr>
              <tr>
                <td>💺 Seats</td>
                <td>
                  {summary.seats.join(", ")}{" "}
                  <span style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>
                    ({summary.seatCategory})
                  </span>
                </td>
              </tr>
              <tr>
                <td>💳 Payment</td>
                <td>{summary.paymentMethod}</td>
              </tr>

              {/* Price breakdown */}
              <tr>
                <td style={{ paddingTop: "0.85rem", color: "var(--text-muted)", fontSize: "0.78rem" }}>
                  Base price
                </td>
                <td style={{ paddingTop: "0.85rem", fontSize: "0.85rem" }}>
                  ₹{summary.pricePerSeat} × {summary.quantity} = ₹{summary.pricePerSeat * summary.quantity}
                </td>
              </tr>
              <tr>
                <td style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Convenience fee</td>
                <td style={{ fontSize: "0.85rem" }}>₹{summary.convenienceFee}</td>
              </tr>
              <tr>
                <td style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>GST (18%)</td>
                <td style={{ fontSize: "0.85rem" }}>₹{summary.gst}</td>
              </tr>
              <tr className="booking-total-row">
                <td>💰 Total Payable</td>
                <td>
                  <span className="booking-total-amount">₹{summary.total}</span>
                </td>
              </tr>
            </tbody>
          </table>

          {/* Budget check */}
          <div className={`budget-check-row ${withinBudget ? "budget-ok" : "budget-fail"}`}
               role="status">
            {withinBudget ? (
              <>✅ Within budget · Saving ₹{savings.toFixed(0)} from your ₹{summary.budgetLimit} limit</>
            ) : (
              <>❌ Exceeds budget by ₹{Math.abs(savings).toFixed(0)} (limit: ₹{summary.budgetLimit})</>
            )}
          </div>

          {/* Action buttons */}
          <div className="modal-actions">
            <button
              id="approve-payment-btn"
              className="btn-approve"
              onClick={onApprove}
              disabled={isLoading}
              aria-label="Approve and proceed with simulated payment"
            >
              {isLoading ? (
                <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}>
                  <span className="btn-spinner" />
                  Processing…
                </span>
              ) : (
                "✅ Approve & Pay"
              )}
            </button>
            <button
              id="cancel-payment-btn"
              className="btn-cancel"
              onClick={onCancel}
              disabled={isLoading}
              aria-label="Cancel task"
            >
              ❌ Cancel
            </button>
          </div>

          {/* Demo note */}
          <p className="modal-demo-note" role="note">
            ⚠️ DEMO MODE — No real payment will be processed
          </p>
        </div>
      </div>
    </div>
  );
}
