export type Kpi = {
  id: string;
  label: string;
  value: string;
  compare: string;
  /** 0-100 for progress bar visualization */
  percent?: number;
  trend?: "up" | "down" | "flat";
  icon?: string;
};

export type Priority = {
  id: "energy" | "sea" | "industry";
  title: string;
  weight: "خیلی بالا" | "بالا" | "متوسط";
  /** 0-100 for weight bar visualization */
  weightPercent: number;
  role: string;
  roleIcon?: string;
  horizon: string;
  colorKey: "red" | "blue" | "yellow";
  issues: { id: string; text: string }[];
  tech: string;
};

export type TechItem = {
  id: string;
  priority: "energy" | "sea" | "industry";
  label: string;
  detail: string;
  colorKey: "red" | "blue" | "yellow";
};

export type BushehrAtAGlance = {
  title: string;
  mission: string;
  kpis: Kpi[];
  priorities: Priority[];
  techItems: TechItem[];
  updatedAt?: string;
};