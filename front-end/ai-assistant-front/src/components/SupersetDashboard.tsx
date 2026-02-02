import React, { useEffect, useRef, useState } from "react";
import { embedDashboard } from "@superset-ui/embedded-sdk";
import supersetService from "../services/supersetService";

interface SupersetDashboardProps {
  /**
   * UUID from Superset "Embed" panel (required)
   */
  dashboardUuid: string;

  className?: string;

  onDashboardLoad?: () => void;
  onDashboardError?: (errorMessage: string) => void;
}

const SupersetDashboard: React.FC<SupersetDashboardProps> = ({
  dashboardUuid,
  className = "",
  onDashboardLoad,
  onDashboardError,
}) => {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    const run = async () => {
      try {
        setLoading(true);
        setError(null);

        if (!mountRef.current) return;

        // Clean mount point on re-render to avoid duplicate iframes
        mountRef.current.innerHTML = "";

        // 1) Ask backend for guest token + superset_domain
        const { superset_domain } = await supersetService.generateGuestToken({
          dashboard_uuid: dashboardUuid,
        });

        // 2) Embed the dashboard using Superset Embedded SDK
        await embedDashboard({
          id: dashboardUuid,
          supersetDomain: superset_domain,
          mountPoint: mountRef.current,

          // SDK will call this whenever it needs a fresh token
          fetchGuestToken: async () => {
            const res = await supersetService.generateGuestToken({
              dashboard_uuid: dashboardUuid,
            });
            return res.token;
          },

          // Optional UI config
          dashboardUiConfig: {
            hideTitle: false,
            hideChartControls: false,
            hideTab: false,
          },
        });

        if (!isCancelled) {
          setLoading(false);
          onDashboardLoad?.();
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to embed dashboard";
        if (!isCancelled) {
          setLoading(false);
          setError(msg);
          onDashboardError?.(msg);
        }
      }
    };

    run();

    return () => {
      isCancelled = true;
      // Optional cleanup: remove iframe content
      if (mountRef.current) mountRef.current.innerHTML = "";
    };
  }, [dashboardUuid, onDashboardLoad, onDashboardError]);

  if (loading) {
    return (
      <div className={`superset-embed-loading ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`superset-embed-error ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-red-600 font-medium mb-2">Error loading dashboard</p>
            <p className="text-gray-500 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // The SDK will mount an iframe into this div
  return <div ref={mountRef} className={`superset-embed ${className}`} style={{ minHeight: 600 }} />;
};

export default SupersetDashboard;
