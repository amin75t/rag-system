import type { Kpi } from "../types/bushehr";
import { kpiIconMap } from "./Icons";

const trendColor: Record<string, string> = {
  up: "text-emerald-600",
  down: "text-rose-500",
  flat: "text-neutral-400",
};
const trendArrow: Record<string, string> = {
  up: "\u25B2",
  down: "\u25BC",
  flat: "\u25CF",
};
const trendBg: Record<string, string> = {
  up: "bg-emerald-50",
  down: "bg-rose-50",
  flat: "bg-neutral-50",
};

const barColor: Record<string, string> = {
  up: "bg-gradient-to-l from-emerald-400 to-emerald-500",
  down: "bg-gradient-to-l from-rose-400 to-rose-500",
  flat: "bg-gradient-to-l from-sky-400 to-sky-500",
};

export function KpiCard({ kpi }: { kpi: Kpi }) {
  const Icon = kpi.icon ? kpiIconMap[kpi.icon] : null;
  const trend = kpi.trend ?? "flat";

  return (
    <div className="group relative flex items-start gap-3 rounded-2xl border border-neutral-200/70 bg-white p-4 shadow-sm transition-all duration-300 hover:shadow-lg hover:border-sky-200 hover:-translate-y-0.5 animate-scale-in">
      {/* icon */}
      {Icon && (
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-sky-50 to-sky-100 text-sky-600 shadow-sm transition-all duration-300 group-hover:shadow-md group-hover:scale-105">
          <Icon className="w-5 h-5" />
        </div>
      )}

      {/* content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium text-neutral-500">{kpi.label}</span>
          {kpi.trend && (
            <span className={`inline-flex items-center justify-center rounded-full px-1.5 py-0.5 text-[9px] font-bold ${trendColor[trend]} ${trendBg[trend]}`}>
              {trendArrow[trend]}
            </span>
          )}
        </div>
        <div className="mt-1 text-lg font-extrabold text-neutral-900 leading-tight">
          {kpi.value}
        </div>

        {/* progress bar */}
        {kpi.percent != null && (
          <div className="mt-2.5 h-1.5 w-full rounded-full bg-neutral-100 overflow-hidden">
            <div
              className={`h-full rounded-full animate-bar-fill ${barColor[trend]}`}
              style={{ width: `${kpi.percent}%` }}
            />
          </div>
        )}

        {kpi.compare && (
          <div className="mt-2 text-[10px] text-neutral-500 leading-relaxed">
            {kpi.compare}
          </div>
        )}
      </div>
    </div>
  );
}
