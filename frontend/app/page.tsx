"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, DashboardData } from "./lib/api";
import MetricCard from "./components/MetricCard";
import AIChat from "./components/AIChat";

// Fallback data when backend is not connected
const FALLBACK_DATA: DashboardData = {
  total_aum: 15847523.5,
  total_clients: 3,
  clients: [
    {
      client_id: "client-001",
      client_name: "John Sharma",
      risk_profile: "aggressive",
      total_invested: 6945000,
      total_current_value: 7842135.5,
      total_pnl: 897135.5,
      total_pnl_pct: 12.92,
      portfolios_count: 2,
    },
    {
      client_id: "client-002",
      client_name: "Priya Mehta",
      risk_profile: "moderate",
      total_invested: 3960000,
      total_current_value: 4389770,
      total_pnl: 429770,
      total_pnl_pct: 10.85,
      portfolios_count: 1,
    },
    {
      client_id: "client-003",
      client_name: "Rahul Patel",
      risk_profile: "conservative",
      total_invested: 2127500,
      total_current_value: 2303320,
      total_pnl: 175820,
      total_pnl_pct: 8.26,
      portfolios_count: 1,
    },
  ],
};

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    api
      .getDashboard()
      .then((d) => {
        setData(d);
        setIsLive(true);
      })
      .catch(() => {
        setData(FALLBACK_DATA);
        setIsLive(false);
      });
  }, []);

  if (!data) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-[var(--muted)]">Loading dashboard...</div>
      </div>
    );
  }

  const formatINR = (n: number) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(n);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Advisor Dashboard</h1>
        <p className="text-sm text-[var(--muted)] mt-1">
          Portfolio management overview
          {!isLive && (
            <span className="ml-2 px-2 py-0.5 bg-[var(--warning)]/20 text-[var(--warning)] text-xs rounded">
              Demo Mode - Start backend for live data
            </span>
          )}
          {isLive && (
            <span className="ml-2 px-2 py-0.5 bg-[var(--success)]/20 text-[var(--success)] text-xs rounded">
              Live
            </span>
          )}
        </p>
      </div>

      {/* Top Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total AUM"
          value={formatINR(data.total_aum)}
          subtitle="Assets Under Management"
          icon={
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          }
        />
        <MetricCard
          title="Total Clients"
          value={data.total_clients.toString()}
          subtitle="Active portfolios"
          icon={
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
            </svg>
          }
        />
        <MetricCard
          title="Total P&L"
          value={formatINR(
            data.clients.reduce((s, c) => s + c.total_pnl, 0)
          )}
          trend={
            data.clients.reduce((s, c) => s + c.total_pnl, 0) /
            data.clients.reduce((s, c) => s + c.total_invested, 0) *
            100
          }
        />
        <MetricCard
          title="Avg Return"
          value={`${(
            data.clients.reduce((s, c) => s + c.total_pnl_pct, 0) /
            data.clients.length
          ).toFixed(2)}%`}
          subtitle="Across all clients"
        />
      </div>

      {/* Client Cards */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white mb-4">Client Portfolios</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {data.clients.map((client) => (
          <Link key={client.client_id} href={`/clients/${client.client_id}`}>
            <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl p-6 hover:border-[var(--accent)] transition-colors cursor-pointer animate-fade-in">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-white">{client.client_name}</h3>
                  <span
                    className={`text-xs px-2 py-0.5 rounded mt-1 inline-block ${
                      client.risk_profile === "aggressive"
                        ? "bg-[var(--danger)]/20 text-[var(--danger)]"
                        : client.risk_profile === "moderate"
                        ? "bg-[var(--warning)]/20 text-[var(--warning)]"
                        : "bg-[var(--success)]/20 text-[var(--success)]"
                    }`}
                  >
                    {client.risk_profile}
                  </span>
                </div>
                <span className="text-xs text-[var(--muted)]">
                  {client.portfolios_count} portfolio{client.portfolios_count !== 1 ? "s" : ""}
                </span>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-[var(--muted)]">Invested</span>
                  <span className="text-white font-mono">{formatINR(client.total_invested)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-[var(--muted)]">Current</span>
                  <span className="text-white font-mono">{formatINR(client.total_current_value)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-[var(--muted)]">P&L</span>
                  <span
                    className={`font-mono font-medium ${
                      client.total_pnl >= 0 ? "text-[var(--success)]" : "text-[var(--danger)]"
                    }`}
                  >
                    {client.total_pnl >= 0 ? "+" : ""}
                    {formatINR(client.total_pnl)} ({client.total_pnl_pct.toFixed(2)}%)
                  </span>
                </div>
              </div>

              {/* Mini progress bar */}
              <div className="mt-4 h-1.5 bg-[var(--card-border)] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--success)]"
                  style={{
                    width: `${Math.min(100, Math.max(0, client.total_pnl_pct * 5))}%`,
                  }}
                />
              </div>
            </div>
          </Link>
        ))}
      </div>

      <AIChat />
    </div>
  );
}
