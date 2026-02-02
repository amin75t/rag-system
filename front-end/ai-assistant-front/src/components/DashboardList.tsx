import React, { useEffect, useState } from "react";
import supersetService, { EmbeddedDashboard } from "../services/supersetService";
import SupersetDashboard from "./SupersetDashboard";

interface DashboardListProps {
  className?: string;
}

const DashboardList: React.FC<DashboardListProps> = ({ className = "" }) => {
  const [dashboards, setDashboards] = useState<EmbeddedDashboard[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDashboard, setSelectedDashboard] = useState<EmbeddedDashboard | null>(null);

  useEffect(() => {
    const fetchDashboards = async () => {
      try {
        setLoading(true);
        setError(null);
        const dashboardList = await supersetService.getEmbeddedDashboards();
        setDashboards(dashboardList);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to fetch dashboards";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboards();
  }, []);

  const handleDashboardSelect = (dashboard: EmbeddedDashboard) => {
    setSelectedDashboard(dashboard);
  };

  const handleBackToList = () => {
    setSelectedDashboard(null);
  };

  if (loading) {
    return (
      <div className={`dashboard-list-loading ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboards...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`dashboard-list-error ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-red-500 mb-4">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <p className="text-red-600 font-medium mb-2">Error loading dashboards</p>
            <p className="text-gray-500 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (selectedDashboard) {
    return (
      <div className={`dashboard-view ${className}`}>
        <div className="mb-4">
          <button
            onClick={handleBackToList}
            className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard List
          </button>

          <h2 className="text-2xl font-bold mt-2">{selectedDashboard.name}</h2>
        </div>

        <SupersetDashboard
          dashboardUuid={selectedDashboard.dashboard_uuid}
          onDashboardLoad={() => console.log("Dashboard loaded successfully")}
          onDashboardError={(errMsg) => console.error("Dashboard error:", errMsg)}
        />
      </div>
    );
  }

  return (
    <div className={`dashboard-list ${className}`}>
      <h2 className="text-2xl font-bold mb-6">Available Dashboards</h2>

      {dashboards.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <p className="text-gray-500">No dashboards available</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboards.map((dashboard) => (
            <div
              key={dashboard.id}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border border-gray-200"
              onClick={() => handleDashboardSelect(dashboard)}
            >
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      />
                    </svg>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{dashboard.name}</h3>

                    {/* Show numeric Superset id if available, otherwise show UUID */}
                    <p className="text-sm text-gray-500">
                      {dashboard.superset_dashboard_id
                        ? `Superset ID: ${dashboard.superset_dashboard_id}`
                        : `UUID: ${dashboard.dashboard_uuid}`}
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
                      />
                    </svg>
                    {dashboard.domain}
                  </div>

                  <div className="flex items-center text-sm text-gray-600">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                      />
                    </svg>
                    {dashboard.allowed_roles.join(", ") || "Public"}
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-xs text-gray-400">
                    Created: {new Date(dashboard.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DashboardList;
