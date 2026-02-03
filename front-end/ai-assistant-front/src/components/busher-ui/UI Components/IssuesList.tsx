
import { Priority } from "../../../types/bushehr";
import { IconWarning } from "./Icons";

const colorMap: Record<
  Priority["colorKey"],
  { header: string; headerBg: string; dot: string; border: string; bg: string; icon: string; number: string }
> = {
  red: {
    header: "text-red-700",
    headerBg: "bg-red-50",
    dot: "bg-red-400",
    border: "border-red-200/60 hover:border-red-300",
    bg: "bg-red-50/40",
    icon: "text-red-400",
    number: "text-red-300",
  },
  blue: {
    header: "text-blue-700",
    headerBg: "bg-blue-50",
    dot: "bg-blue-400",
    border: "border-blue-200/60 hover:border-blue-300",
    bg: "bg-blue-50/40",
    icon: "text-blue-400",
    number: "text-blue-300",
  },
  yellow: {
    header: "text-yellow-700",
    headerBg: "bg-yellow-50",
    dot: "bg-yellow-400",
    border: "border-yellow-200/60 hover:border-yellow-300",
    bg: "bg-yellow-50/40",
    icon: "text-yellow-500",
    number: "text-yellow-400",
  },
};

const emojiMap: Record<Priority["colorKey"], string> = {
  red: "🔴",
  blue: "🔵",
  yellow: "🟡",
};

export function IssuesList({ p }: { p: Priority }) {
  const c = colorMap[p.colorKey];

  return (
    <div
      className={`rounded-2xl border bg-white shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 animate-scale-in overflow-hidden ${c.border}`}
    >
      {/* header */}
      <div className={`flex items-center gap-2 px-4 py-3 text-sm font-extrabold ${c.header} ${c.headerBg}`}>
        <span>{emojiMap[p.colorKey]}</span>
        {p.title}
        <span className="mr-auto text-[10px] font-medium text-neutral-400">
          {p.issues.length} مورد
        </span>
      </div>

      {/* issues */}
      <ul className="p-3 space-y-1.5">
        {p.issues.map((it: { id: string; text: string }, i: number) => (
          <li
            key={it.id}
            className={`flex items-start gap-2.5 rounded-xl px-3 py-2.5 text-xs text-neutral-700 transition-colors hover:brightness-95 ${c.bg}`}
          >
            <span className={`mt-0.5 text-[10px] font-bold shrink-0 tabular-nums ${c.number}`}>
              {String(i + 1).padStart(2, "0")}
            </span>
            <IconWarning className={`w-3.5 h-3.5 mt-0.5 shrink-0 ${c.icon}`} />
            <span className="leading-relaxed">{it.text}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}