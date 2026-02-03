
import { Priority } from "../../../types/bushehr";
import { priorityIconMap,} from "./iconMaps";
import { IconChip } from "./Icons";

const colorMap: Record<
  Priority["colorKey"],
  {
    card: string;
    border: string;
    badge: string;
    bar: string;
    barTrack: string;
    iconBg: string;
    iconText: string;
    techBg: string;
    techText: string;
    horizonBg: string;
    horizonText: string;
  }
> = {
  red: {
    card: "bg-gradient-to-bl from-red-50/80 via-orange-50/30 to-white",
    border: "border-red-200/60 hover:border-red-300",
    badge: "bg-red-100 text-red-700",
    bar: "bg-gradient-to-l from-red-400 to-red-500",
    barTrack: "bg-red-100",
    iconBg: "bg-gradient-to-br from-red-100 to-red-50",
    iconText: "text-red-600",
    techBg: "bg-red-50 border-red-100",
    techText: "text-red-600",
    horizonBg: "bg-white/80 border-red-100/60",
    horizonText: "text-red-700",
  },
  blue: {
    card: "bg-gradient-to-bl from-blue-50/80 via-cyan-50/30 to-white",
    border: "border-blue-200/60 hover:border-blue-300",
    badge: "bg-blue-100 text-blue-700",
    bar: "bg-gradient-to-l from-blue-400 to-blue-500",
    barTrack: "bg-blue-100",
    iconBg: "bg-gradient-to-br from-blue-100 to-blue-50",
    iconText: "text-blue-600",
    techBg: "bg-blue-50 border-blue-100",
    techText: "text-blue-600",
    horizonBg: "bg-white/80 border-blue-100/60",
    horizonText: "text-blue-700",
  },
  yellow: {
    card: "bg-gradient-to-bl from-yellow-50/80 via-amber-50/30 to-white",
    border: "border-yellow-200/60 hover:border-yellow-300",
    badge: "bg-yellow-100 text-yellow-700",
    bar: "bg-gradient-to-l from-yellow-400 to-amber-500",
    barTrack: "bg-yellow-100",
    iconBg: "bg-gradient-to-br from-yellow-100 to-yellow-50",
    iconText: "text-yellow-700",
    techBg: "bg-yellow-50 border-yellow-100",
    techText: "text-yellow-700",
    horizonBg: "bg-white/80 border-yellow-100/60",
    horizonText: "text-yellow-700",
  },
};

export function PriorityCard({ p }: { p: Priority }) {
  const c = colorMap[p.colorKey];
  const Icon = p.roleIcon ? priorityIconMap[p.roleIcon] : null;

  return (
    <div
      className={`rounded-2xl border p-5 shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 animate-scale-in ${c.card} ${c.border}`}
    >
      {/* header row */}
      <div className="flex items-center gap-3">
        {Icon && (
          <div
            className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl shadow-sm ${c.iconBg} ${c.iconText}`}
          >
            <Icon className="w-6 h-6" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-base font-extrabold text-neutral-900">
              {p.title}
            </span>
            <span
              className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold shadow-sm ${c.badge}`}
            >
              {p.weight}
            </span>
          </div>
          <div className="mt-0.5 text-[11px] text-neutral-500">
            نقش: <span className="font-semibold text-neutral-600">{p.role}</span>
          </div>
        </div>
      </div>

      {/* weight bar */}
      <div className="mt-4">
        <div className="flex items-center justify-between text-[10px] text-neutral-500 mb-1.5">
          <span>وزن راهبردی</span>
          <span className="font-bold text-neutral-700">{p.weightPercent}٪</span>
        </div>
        <div className={`h-2.5 w-full rounded-full overflow-hidden ${c.barTrack}`}>
          <div
            className={`h-full rounded-full animate-bar-fill ${c.bar}`}
            style={{ width: `${p.weightPercent}%` }}
          />
        </div>
      </div>

      {/* horizon + tech row */}
      <div className="mt-4 flex flex-wrap items-center gap-2">
        <div className={`rounded-lg border px-3 py-1.5 text-[11px] ${c.horizonBg}`}>
          <span className="text-neutral-400">افق: </span>
          <span className={`font-semibold ${c.horizonText}`}>{p.horizon}</span>
        </div>
        <div
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[10px] font-medium ${c.techBg} ${c.techText}`}
        >
          <IconChip className="w-3.5 h-3.5" />
          {p.tech}
        </div>
      </div>
    </div>
  );
}