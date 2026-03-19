"use client";

import { HoldingDetail } from "../lib/api";

interface HoldingsTableProps {
  holdings: HoldingDetail[];
}

export default function HoldingsTable({ holdings }: HoldingsTableProps) {
  const formatINR = (n: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

  return (
    <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl overflow-hidden animate-fade-in">
      <div className="p-6 border-b border-[var(--card-border)]">
        <h3 className="text-sm font-medium text-[var(--muted)]">Holdings</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--card-border)]">
              <th className="text-left p-4 text-[var(--muted)] font-medium">Symbol</th>
              <th className="text-left p-4 text-[var(--muted)] font-medium">Name</th>
              <th className="text-left p-4 text-[var(--muted)] font-medium">Type</th>
              <th className="text-right p-4 text-[var(--muted)] font-medium">Qty</th>
              <th className="text-right p-4 text-[var(--muted)] font-medium">Avg Price</th>
              <th className="text-right p-4 text-[var(--muted)] font-medium">Current</th>
              <th className="text-right p-4 text-[var(--muted)] font-medium">Value</th>
              <th className="text-right p-4 text-[var(--muted)] font-medium">P&L</th>
              <th className="text-right p-4 text-[var(--muted)] font-medium">P&L %</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((h) => (
              <tr key={h.id} className="border-b border-[var(--card-border)] hover:bg-[var(--card-border)]/30 transition-colors">
                <td className="p-4 font-mono font-bold text-white">{h.symbol}</td>
                <td className="p-4 text-[var(--foreground)]">{h.name}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    h.asset_type === "equity"
                      ? "bg-[var(--accent)]/20 text-[var(--accent-light)]"
                      : h.asset_type === "debt"
                      ? "bg-[var(--warning)]/20 text-[var(--warning)]"
                      : "bg-[var(--success)]/20 text-[var(--success)]"
                  }`}>
                    {h.asset_type.replace(/_/g, " ")}
                  </span>
                </td>
                <td className="p-4 text-right font-mono">{h.quantity}</td>
                <td className="p-4 text-right font-mono">{formatINR(h.avg_buy_price)}</td>
                <td className="p-4 text-right font-mono">{formatINR(h.current_price)}</td>
                <td className="p-4 text-right font-mono font-medium text-white">{formatINR(h.current_value)}</td>
                <td className={`p-4 text-right font-mono font-medium ${
                  h.pnl >= 0 ? "text-[var(--success)]" : "text-[var(--danger)]"
                }`}>
                  {h.pnl >= 0 ? "+" : ""}{formatINR(h.pnl)}
                </td>
                <td className={`p-4 text-right font-mono font-medium ${
                  h.pnl_pct >= 0 ? "text-[var(--success)]" : "text-[var(--danger)]"
                }`}>
                  {h.pnl_pct >= 0 ? "+" : ""}{h.pnl_pct.toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
