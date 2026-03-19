const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

// Types
export interface Client {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  risk_profile: string;
  target_equity_pct: number;
  target_debt_pct: number;
}

export interface DashboardData {
  total_aum: number;
  total_clients: number;
  clients: {
    client_id: string;
    client_name: string;
    risk_profile: string;
    total_invested: number;
    total_current_value: number;
    total_pnl: number;
    total_pnl_pct: number;
    portfolios_count: number;
  }[];
}

export interface PortfolioSummary {
  portfolio_id: string;
  portfolio_name: string;
  client_id: string;
  summary: {
    total_invested: number;
    total_current_value: number;
    total_pnl: number;
    total_pnl_pct: number;
    xirr: number | null;
    cagr: number | null;
    holdings_count: number;
  };
  asset_allocation: Record<string, number>;
  asset_allocation_value: Record<string, number>;
  sector_allocation: Record<string, number>;
  sector_allocation_value: Record<string, number>;
  holdings: HoldingDetail[];
}

export interface HoldingDetail {
  id: string;
  symbol: string;
  name: string;
  asset_type: string;
  sector: string;
  quantity: number;
  avg_buy_price: number;
  current_price: number;
  invested_value: number;
  current_value: number;
  pnl: number;
  pnl_pct: number;
}

export interface ClientSummary {
  client_id: string;
  total_invested: number;
  total_current_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  portfolios: PortfolioSummary[];
}

export interface AgentResponse {
  response: string;
  actions_taken: Record<string, unknown>[];
  context_used: string[];
}

// API functions
export const api = {
  getDashboard: () => apiFetch<DashboardData>("/analytics/dashboard"),
  getClients: () => apiFetch<Client[]>("/clients/"),
  getClient: (id: string) => apiFetch<Client>(`/clients/${id}`),
  getClientSummary: (id: string) => apiFetch<ClientSummary>(`/clients/${id}/summary`),
  getPortfolio: (id: string) => apiFetch<PortfolioSummary>(`/portfolios/${id}`),
  chatWithAgent: (message: string, clientId?: string) =>
    apiFetch<AgentResponse>("/agent/chat", {
      method: "POST",
      body: JSON.stringify({ message, client_id: clientId }),
    }),
};
