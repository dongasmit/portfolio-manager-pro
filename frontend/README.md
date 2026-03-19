# Frontend — Next.js Portfolio Manager

A modern, dark-themed dashboard for the Agentic AI Portfolio Manager. Built with **Next.js 16**, **React 19**, and **Tailwind CSS 4**.

## Tech Stack

- **Framework:** Next.js 16 (App Router, Turbopack)
- **UI:** React 19, Tailwind CSS 4
- **Charts:** Recharts
- **API Client:** Typed fetch wrapper with environment-aware base URL

## Features

- **Dashboard** — Total AUM, client overview, P&L at a glance
- **Client Portfolios** — Detailed holdings tables with XIRR, CAGR metrics
- **Charts** — Asset allocation (pie), sector allocation (pie), performance
- **AI Chat** — Floating chat widget connected to the backend AI agent
- **Dark Theme** — Premium glassmorphism UI with smooth animations

## Pages

| Route | Description |
|---|---|
| `/` | Dashboard — AUM overview, all clients |
| `/clients` | Client list |
| `/clients/[id]` | Client detail — portfolios, holdings, charts |

## Local Setup

```bash
npm install
npm run dev
```

Open **http://localhost:3000**

The frontend expects the backend at `http://localhost:8000/api` by default. Override with the `NEXT_PUBLIC_API_URL` environment variable.

## Deploy to Vercel

1. Import the GitHub repo on [vercel.com](https://vercel.com)
2. Set **Root Directory** to `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-render-backend.onrender.com/api`
4. Deploy

## Components

| Component | Description |
|---|---|
| `AIChat.tsx` | Floating AI chat widget with message history |
| `AllocationChart.tsx` | Recharts pie chart for asset/sector allocation |
| `HoldingsTable.tsx` | Sortable table for portfolio holdings |
| `MetricCard.tsx` | Stat card with label, value, and change indicator |
| `Sidebar.tsx` | Navigation sidebar with Dashboard/Clients links |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api` | Backend API base URL |
