import type { BushehrAtAGlance } from "../types/bushehr";


export async function fetchBushehrAtAGlance(): Promise<BushehrAtAGlance> {
  const res = await fetch("/api/bushehr/at-a-glance"); // بعداً بک می‌دی
  if (!res.ok) throw new Error("Failed to fetch data");
  return res.json();
}