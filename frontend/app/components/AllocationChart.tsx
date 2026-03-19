"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4", "#ec4899", "#8b5cf6", "#14b8a6"];

interface AllocationChartProps {
  data: Record<string, number>;
  title: string;
}

export default function AllocationChart({ data, title }: AllocationChartProps) {
  const chartData = Object.entries(data)
    .filter(([, value]) => value > 0)
    .map(([name, value]) => ({
      name: name.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
      value: Math.round(value * 100) / 100,
    }));

  if (chartData.length === 0) {
    return (
      <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl p-6">
        <h3 className="text-sm font-medium text-[var(--muted)] mb-4">{title}</h3>
        <p className="text-sm text-[var(--muted)]">No data available</p>
      </div>
    );
  }

  return (
    <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl p-6 animate-fade-in">
      <h3 className="text-sm font-medium text-[var(--muted)] mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--card-bg)",
              border: "1px solid var(--card-border)",
              borderRadius: "8px",
              color: "var(--foreground)",
            }}
            formatter={(value) => [`${value}%`, ""]}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value) => <span style={{ color: "var(--foreground)", fontSize: "12px" }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
