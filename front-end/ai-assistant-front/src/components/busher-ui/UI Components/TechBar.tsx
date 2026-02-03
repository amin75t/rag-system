
import { TechItem } from "../../../types/bushehr";
import { IconChip } from "./Icons";

const colorMap: Record<
  TechItem["colorKey"],
  { bg: string; border: string; label: string; icon: string; iconBg: string }
> = {
  red: {
    bg: "bg-gradient-to-br from-red-50 to-red-50/50",
    border: "border-red-200/60 hover:border-red-300",
    label: "text-red-700",
    icon: "text-red-500",
    iconBg: "bg-red-100",
  },
  blue: {
    bg: "bg-gradient-to-br from-blue-50 to-blue-50/50",
    border: "border-blue-200/60 hover:border-blue-300",
    label: "text-blue-700",
    icon: "text-blue-500",
    iconBg: "bg-blue-100",
  },
  yellow: {
    bg: "bg-gradient-to-br from-yellow-50 to-yellow-50/50",
    border: "border-yellow-200/60 hover:border-yellow-300",
    label: "text-yellow-700",
    icon: "text-yellow-600",
    iconBg: "bg-yellow-100",
  },
};

export function TechBar({ items }: { items: TechItem[] }) {
  return (
    <div className="rounded-2xl border border-neutral-200/60 bg-white p-5 shadow-sm animate-scale-in">
      <div className="flex items-center gap-2.5 text-sm font-extrabold text-neutral-800">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50">
          <IconChip className="w-4.5 h-4.5 text-violet-500" />
        </div>
        لایه نوظهور فناوری
      </div>
      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        {items.map((t) => {
          const c = colorMap[t.colorKey];
          return (
            <div
              key={t.id}
              className={`flex items-start gap-3 rounded-xl border px-4 py-3.5 transition-all duration-300 hover:shadow-md hover:-translate-y-0.5 ${c.bg} ${c.border}`}
            >
              <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${c.iconBg}`}>
                <IconChip className={`w-4 h-4 ${c.icon}`} />
              </div>
              <div>
                <div className={`text-xs font-bold ${c.label}`}>{t.label}</div>
                <div className="mt-1 text-[11px] text-neutral-600 leading-relaxed">
                  {t.detail}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}