interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  trend?: number;
  icon?: React.ReactNode;
}

export default function MetricCard({ title, value, subtitle, trend, icon }: MetricCardProps) {
  return (
    <div className="bg-[var(--card-bg)] border border-[var(--card-border)] rounded-xl p-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-[var(--muted)] mb-1">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-[var(--muted)] mt-1">{subtitle}</p>}
          {trend !== undefined && (
            <p
              className={`text-sm mt-2 font-medium ${
                trend >= 0 ? "text-[var(--success)]" : "text-[var(--danger)]"
              }`}
            >
              {trend >= 0 ? "+" : ""}
              {trend.toFixed(2)}%
            </p>
          )}
        </div>
        {icon && (
          <div className="p-3 rounded-lg bg-[var(--accent)]/10 text-[var(--accent-light)]">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
