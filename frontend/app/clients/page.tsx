"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Client } from "../lib/api";

const FALLBACK_CLIENTS: Client[] = [
  { id: "client-001", name: "John Sharma", email: "john.sharma@example.com", phone: "+91 98765 43210", risk_profile: "aggressive", target_equity_pct: 70, target_debt_pct: 30 },
  { id: "client-002", name: "Priya Mehta", email: "priya.mehta@example.com", phone: "+91 87654 32109", risk_profile: "moderate", target_equity_pct: 60, target_debt_pct: 40 },
  { id: "client-003", name: "Rahul Patel", email: "rahul.patel@example.com", phone: "+91 76543 21098", risk_profile: "conservative", target_equity_pct: 40, target_debt_pct: 60 },
];

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);

  useEffect(() => {
    api.getClients().then(setClients).catch(() => setClients(FALLBACK_CLIENTS));
  }, []);

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Clients</h1>
        <p className="text-sm text-[var(--muted)] mt-1">Manage client portfolios</p>
      </div>

      <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--card-border)]">
              <th className="text-left p-4 text-[var(--muted)] font-medium">Name</th>
              <th className="text-left p-4 text-[var(--muted)] font-medium">Email</th>
              <th className="text-left p-4 text-[var(--muted)] font-medium">Risk Profile</th>
              <th className="text-left p-4 text-[var(--muted)] font-medium">Target Allocation</th>
              <th className="text-right p-4 text-[var(--muted)] font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {clients.map((client) => (
              <tr key={client.id} className="border-b border-[var(--card-border)] hover:bg-[var(--card-border)]/30 transition-colors">
                <td className="p-4 font-medium text-white">{client.name}</td>
                <td className="p-4 text-[var(--foreground)]">{client.email}</td>
                <td className="p-4">
                  <span className={`text-xs px-2 py-1 rounded font-medium ${
                    client.risk_profile === "aggressive"
                      ? "bg-[var(--danger)]/20 text-[var(--danger)]"
                      : client.risk_profile === "moderate"
                      ? "bg-[var(--warning)]/20 text-[var(--warning)]"
                      : "bg-[var(--success)]/20 text-[var(--success)]"
                  }`}>
                    {client.risk_profile}
                  </span>
                </td>
                <td className="p-4 text-[var(--foreground)] font-mono text-xs">
                  Eq {client.target_equity_pct}% / Debt {client.target_debt_pct}%
                </td>
                <td className="p-4 text-right">
                  <Link
                    href={`/clients/${client.id}`}
                    className="px-3 py-1.5 bg-[var(--accent)] text-white rounded-lg text-xs font-medium hover:bg-[var(--accent-light)] transition-colors"
                  >
                    View Portfolio
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
