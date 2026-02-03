// hooks/useBushehrAtAGlance.ts
import { useEffect, useState } from "react";

import { bushehrMock } from "../mock/bushehr";
import { fetchBushehrAtAGlance } from "../services/bushehr.service";
import type { BushehrAtAGlance } from "../types/bushehr";

export function useBushehrAtAGlance(mode: "mock" | "api" = "mock") {
  const [data, setData] = useState<BushehrAtAGlance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        setLoading(true);
        const d = mode === "mock" ? bushehrMock : await fetchBushehrAtAGlance();
        if (mounted) setData(d);
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => { mounted = false; };
  }, [mode]);

  return { data, loading };
}
