"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api, ClientSummary, Client } from "../../lib/api";
import MetricCard from "../../components/MetricCard";
import AllocationChart from "../../components/AllocationChart";
import HoldingsTable from "../../components/HoldingsTable";
import AIChat from "../../components/AIChat";

// Fallback for demo mode
const FALLBACK_CLIENT: Client = {
  id: "client-001",
  name: "John Sharma",
  email: "john.sharma@example.com",
  phone: "+91 98765 43210",
  risk_profile: "aggressive",
  target_equity_pct: 70,
  target_debt_pct: 30,
};

const FALLBACK_SUMMARY: ClientSummary = {
  client_id: "client-001",
  total_invested: 6945000,
  total_current_value: 7842135.5,
  total_pnl: 897135.5,
  total_pnl_pct: 12.92,
  portfolios: [
    {
      portfolio_id: "port-001",
      portfolio_name: "Growth Portfolio",
      client_id: "client-001",
      summary: {
        total_invested: 5230000,
        total_current_value: 5912895,
        total_pnl: 682895,
        total_pnl_pct: 13.06,
        xirr: 15.2,
        cagr: 12.8,
        holdings_count: 5,
      },
      asset_allocation: { equity: 100 },
      asset_allocation_value: { equity: 5912895 },
      sector_allocation: { technology: 34, energy: 25, telecom: 11, consumer_discretionary: 17, other: 13 },
      sector_allocation_value: {},
      holdings: [
        { id: "1", symbol: "RELIANCE", name: "Reliance Industries", asset_type: "equity", sector: "energy", quantity: 50, avg_buy_price: 2650, current_price: 2945.5, invested_value: 132500, current_value: 147275, pnl: 14775, pnl_pct: 11.15 },
        { id: "2", symbol: "TCS", name: "Tata Consultancy", asset_type: "equity", sector: "technology", quantity: 30, avg_buy_price: 3800, current_price: 4123.75, invested_value: 114000, current_value: 123712.5, pnl: 9712.5, pnl_pct: 8.52 },
        { id: "3", symbol: "INFY", name: "Infosys", asset_type: "equity", sector: "technology", quantity: 80, avg_buy_price: 1650, current_price: 1856.4, invested_value: 132000, current_value: 148512, pnl: 16512, pnl_pct: 12.51 },
        { id: "4", symbol: "BHARTIARTL", name: "Bharti Airtel", asset_type: "equity", sector: "telecom", quantity: 40, avg_buy_price: 1450, current_price: 1645.3, invested_value: 58000, current_value: 65812, pnl: 7812, pnl_pct: 13.47 },
        { id: "5", symbol: "TATAMOTORS", name: "Tata Motors", asset_type: "equity", sector: "consumer_discretionary", quantity: 100, avg_buy_price: 850, current_price: 987.4, invested_value: 85000, current_value: 98740, pnl: 13740, pnl_pct: 16.16 },
      ],
    },
  ],
};

export default function ClientDetailPage() {
  const params = useParams();
  const clientId = params.id as string;

  const [client, setClient] = useState<Client | null>(null);
  const [summary, setSummary] = useState<ClientSummary | null>(null);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    Promise.all([api.getClient(clientId), api.getClientSummary(clientId)])
      .then(([c, s]) => {
        setClient(c);
        setSummary(s);
        setIsLive(true);
      })
      .catch(() => {
        setClient(FALLBACK_CLIENT);
        setSummary(FALLBACK_SUMMARY);
        setIsLive(false);
      });
  }, [clientId]);

  if (!client || !summary) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-[var(--muted)]">Loading client data...</div>
      </div>
    );
  }

  const formatINR = (n: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Breadcrumb */}
      <div className="mb-6 flex items-center gap-2 text-sm">
        <Link href="/" className="text-[var(--muted)] hover:text-white transition-colors">
          Dashboard
        </Link>
        <span className="text-[var(--muted)]">/</span>
        <Link href="/clients" className="text-[var(--muted)] hover:text-white transition-colors">
          Clients
        </Link>
        <span className="text-[var(--muted)]">/</span>
        <span className="text-white">{client.name}</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">{client.name}</h1>
          <div className="flex items-center gap-3 mt-2">
            <span
              className={`text-xs px-2 py-0.5 rounded font-medium ${
                client.risk_profile === "aggressive"
                  ? "bg-[var(--danger)]/20 text-[var(--danger)]"
                  : client.risk_profile === "moderate"
                  ? "bg-[var(--warning)]/20 text-[var(--warning)]"
                  : "bg-[var(--success)]/20 text-[var(--success)]"
              }`}
            >
              {client.risk_profile}
            </span>
            <span className="text-xs text-[var(--muted)]">
              Target: Eq {client.target_equity_pct}% / Debt {client.target_debt_pct}%
            </span>
            {!isLive && (
              <span className="px-2 py-0.5 bg-[var(--warning)]/20 text-[var(--warning)] text-xs rounded">
                Demo
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard title="Total Invested" value={formatINR(summary.total_invested)} />
        <MetricCard
          title="Current Value"
          value={formatINR(summary.total_current_value)}
          trend={summary.total_pnl_pct}
        />
        <MetricCard
          title="Total P&L"
          value={formatINR(summary.total_pnl)}
          trend={summary.total_pnl_pct}
        />
        <MetricCard
          title="Portfolios"
          value={summary.portfolios.length.toString()}
          subtitle="Active portfolios"
        />
      </div>

      {/* Per-portfolio details */}
      {summary.portfolios.map((portfolio) => (
        <div key={portfolio.portfolio_id} className="mb-10">
          <h2 className="text-lg font-semibold text-white mb-4">{portfolio.portfolio_name}</h2>

          {/* Portfolio metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <MetricCard title="Invested" value={formatINR(portfolio.summary.total_invested)} />
            <MetricCard
              title="Current"
              value={formatINR(portfolio.summary.total_current_value)}
              trend={portfolio.summary.total_pnl_pct}
            />
            {portfolio.summary.xirr !== null && (
              <MetricCard
                title="XIRR"
                value={`${portfolio.summary.xirr}%`}
                subtitle="Annualized return"
              />
            )}
            {portfolio.summary.cagr !== null && (
              <MetricCard
                title="CAGR"
                value={`${portfolio.summary.cagr}%`}
                subtitle="Compound growth"
              />
            )}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <AllocationChart data={portfolio.asset_allocation} title="Asset Allocation" />
            <AllocationChart data={portfolio.sector_allocation} title="Sector Allocation" />
          </div>

          {/* Holdings Table */}
          <HoldingsTable holdings={portfolio.holdings} />
        </div>
      ))}

      <AIChat clientId={clientId} />
    </div>
  );
}
