import { bushehrMock } from "../mock/bushehr";
import { IssuesList } from "../UI Components/IssuesList";
import { KpiCard } from "../UI Components/KpiCard";
import { PriorityCard } from "../UI Components/PriorityCard";
import { TechBar } from "../UI Components/TechBar";

export default function BushehrAtAGlancePage() {
  const data = bushehrMock;

  return (

<div className="min-h-screen bg-gradient-to-b from-slate-50 via-slate-50 to-sky-50/30" dir="rtl">
      {/* ═══════════ بالای صفحه: عنوان + مأموریت ═══════════ */}
      <header className="relative overflow-hidden bg-gradient-to-l from-sky-700 via-sky-800 to-sky-900 px-6 py-8 text-white shadow-xl">
        {/* decorative circles */}
        <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-white/5" />
        <div className="pointer-events-none absolute -bottom-16 left-1/3 h-48 w-48 rounded-full bg-sky-400/10" />
        <div className="pointer-events-none absolute -right-10 top-4 h-32 w-32 rounded-full bg-sky-300/8" />

        <div className="relative mx-auto max-w-7xl animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15 backdrop-blur-sm">
              <svg className="h-7 w-7 text-sky-200" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
                <line x1="8" y1="2" x2="8" y2="18" />
                <line x1="16" y1="6" x2="16" y2="22" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight sm:text-3xl">{data.title}</h1>
              <p className="mt-1 max-w-3xl text-sm leading-relaxed text-sky-100/90">
                {data.mission}
              </p>
            </div>
          </div>
          {data.updatedAt && (
            <span className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3.5 py-1.5 text-[11px] font-medium text-sky-200 backdrop-blur-sm">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-400 animate-[pulse-soft_2s_ease-in-out_infinite]" />
              آخرین بروزرسانی: {data.updatedAt}
            </span>
          )}
        </div>
      </header>

      {/* ═══════════ بدنه اصلی: سه منظر تو در تو ═══════════ */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        {/* ── راهنمای منظرها ── */}
        <div className="mb-6 flex flex-wrap items-center gap-3 text-[11px] font-semibold text-neutral-500 animate-slide-up">
          <Pill color="amber">منظر مسئله‌شناسی</Pill>
          <span className="text-neutral-300">•</span>
          <Pill color="violet">منظر راهبردی</Pill>
          <span className="text-neutral-300">•</span>
          
          <Pill color="sky">منظر جنرال</Pill>
          
        </div>

        {/* ── سه ستون اصلی ── */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          {/* ── راست: منظر مسئله‌شناسی ── */}
          <section className="lg:col-span-4 space-y-3 animate-slide-up" style={{ animationDelay: "100ms" }}>
            <SectionHeader
              title="مسائل کلیدی"
              subtitle="منظر مسئله‌شناسی — شکاف‌ها و گلوگاه‌ها"
              accent="amber"
            />
            <div className="space-y-3 stagger-children">
              {data.priorities.map((p) => (
                <IssuesList key={p.id} p={p} />
              ))}
            </div>
          </section>

          {/* ── مرکز: منظر راهبردی ── */}
          <section className="lg:col-span-5 space-y-3 animate-slide-up" style={{ animationDelay: "200ms" }}>
            <SectionHeader
              title="سه اولویت راهبردی"
              subtitle="منظر راهبردی — وزن، نقش، افق زمانی"
              accent="violet"
            />
            <div className="space-y-3 stagger-children">
              {data.priorities.map((p) => (
                <PriorityCard key={p.id} p={p} />
              ))}
            </div>
          </section>

          {/* ── چپ: منظر جنرال (داده‌های کلان) ── */}
          <section className="lg:col-span-3 space-y-3 animate-slide-up" style={{ animationDelay: "300ms" }}>
            <SectionHeader
              title="داده‌های کلان و شاخص‌ها"
              subtitle="منظر جنرال"
              accent="sky"
            />
            <div className="space-y-3 stagger-children">
              {data.kpis.map((k) => (
                <KpiCard key={k.id} kpi={k} />
              ))}
            </div>
          </section>
        </div>

        {/* ═══════════ پایین صفحه: لایه فناوری ═══════════ */}
        <div className="mt-8 animate-slide-up" style={{ animationDelay: "400ms" }}>
          <TechBar items={data.techItems} />
        </div>

        {/* ── جمع‌بندی بصری ── */}
        <footer className="mt-8 rounded-2xl border border-neutral-200/60 bg-white/80 px-6 py-5 shadow-sm backdrop-blur-sm animate-fade-in" style={{ animationDelay: "500ms" }}>
          <div className="grid grid-cols-1 gap-4 text-[11px] leading-relaxed text-neutral-600 sm:grid-cols-4">
            <FooterItem color="amber" label="راست" text="مسائل کلیدی → شکاف‌ها و گلوگاه‌ها" />
            <FooterItem color="violet" label="مرکز" text="اولویت‌ها → نقش، وزن، افق زمانی" />
            <FooterItem color="sky" label="چپ" text="داده‌های کلان → پایه و زمینه" />
            <FooterItem color="neutral" label="پایین" text="فناوری نوظهور → توانمندسازها" />
          </div>
        </footer>
      </main>
    </div>
  );
}

/* ── helpers ── */

function FooterItem({ color, label, text }: { color: string; label: string; text: string }) {
  const colors: Record<string, { dot: string; text: string }> = {
    sky: { dot: "bg-sky-500", text: "text-sky-700" },
    violet: { dot: "bg-violet-500", text: "text-violet-700" },
    amber: { dot: "bg-amber-500", text: "text-amber-700" },
    neutral: { dot: "bg-neutral-400", text: "text-neutral-700" },
  };
  const c = colors[color] ?? colors.neutral;
  return (
    <div className="flex items-start gap-2">
      <span className={`mt-1.5 inline-block h-2 w-2 shrink-0 rounded-full ${c.dot}`} />
      <div>
        <span className={`font-bold ${c.text}`}>{label}:</span>{" "}
        <span>{text}</span>
      </div>
    </div>
  );
}

function SectionHeader({
  title,
  subtitle,
  accent,
}: {
  title: string;
  subtitle: string;
  accent: string;
}) {
  const accentBar: Record<string, string> = {
    sky: "bg-sky-500",
    violet: "bg-violet-500",
    amber: "bg-amber-500",
  };
  const accentText: Record<string, string> = {
    sky: "text-sky-700",
    violet: "text-violet-700",
    amber: "text-amber-700",
  };
  const accentBg: Record<string, string> = {
    sky: "bg-sky-50",
    violet: "bg-violet-50",
    amber: "bg-amber-50",
  };

  return (
    <div className={`mb-1 rounded-xl px-3 py-2.5 ${accentBg[accent] ?? "bg-neutral-50"}`}>
      <div className="flex items-center gap-2">
        <span
          className={`inline-block h-5 w-1.5 rounded-full ${accentBar[accent] ?? "bg-neutral-400"}`}
        />
        <h2 className={`text-sm font-extrabold ${accentText[accent] ?? "text-neutral-800"}`}>
          {title}
        </h2>
      </div>
      <p className="mr-3.5 mt-0.5 text-[10px] text-neutral-400">{subtitle}</p>
    </div>
  );
}

function Pill({
  children,
  color,
}: {
  children: React.ReactNode;
  color: string;
}) {
  const styles: Record<string, string> = {
    sky: "bg-sky-50 text-sky-700 border-sky-200 shadow-sky-100/50",
    violet: "bg-violet-50 text-violet-700 border-violet-200 shadow-violet-100/50",
    amber: "bg-amber-50 text-amber-700 border-amber-200 shadow-amber-100/50",
  };
  return (
    <span
      className={`rounded-full border px-3 py-1 shadow-sm ${styles[color] ?? "bg-neutral-50 text-neutral-600 border-neutral-200"}`}
    >
      {children}
    </span>
  );
}
