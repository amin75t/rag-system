import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import supersetService, { EmbeddedDashboard } from "../services/supersetService";
import { useLayoutContext } from "../contexts";

const DashboardListPage: React.FC = () => {
  const { isSidebarOpen, toggleSidebar } = useLayoutContext();
  const [dashboards, setDashboards] = useState<EmbeddedDashboard[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 font-iransans">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto mb-4"></div>
          <p className="text-sky-700">در حال بارگذاری داشبوردها...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 font-iransans">
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
          <p className="text-red-600 font-medium mb-2">خطا در بارگذاری داشبوردها</p>
          <p className="text-sky-600 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 min-h-screen font-iransans" dir="rtl">
      {!isSidebarOpen && (
        <button
          onClick={toggleSidebar}
          className="fixed top-4 right-4 z-50 p-2 bg-sky-800 text-white rounded-md shadow-lg hover:bg-sky-700 transition-colors"
          aria-label="Open menu"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      )}
      <h2 className="text-3xl font-bold mb-8 text-sky-900">داشبوردهای Superset</h2>

      {dashboards.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-sky-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <p className="text-sky-600 text-lg">هیچ داشبوردی موجود نیست</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboards.map((dashboard) => (
            <Link
              key={dashboard.id}
              to={`/dashboard/${dashboard.dashboard_uuid}`}
              className="bg-white/90 backdrop-blur-sm rounded-lg shadow-md hover:shadow-lg transition-all duration-300 cursor-pointer border border-sky-200 block hover:-translate-y-1"
            >
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-sky-100 rounded-lg flex items-center justify-center ml-4">
                    <svg className="w-6 h-6 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      />
                    </svg>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-sky-900">{dashboard.name}</h3>

                    {/* Show numeric Superset id if available, otherwise show UUID */}
                    <p className="text-sm text-sky-600">
                      {dashboard.superset_dashboard_id
                        ? `شناسه Superset: ${dashboard.superset_dashboard_id}`
                        : `UUID: ${dashboard.dashboard_uuid}`}
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center text-sm text-sky-700">
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
                      />
                    </svg>
                    {dashboard.domain}
                  </div>

                  <div className="flex items-center text-sm text-sky-700">
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                      />
                    </svg>
                    {dashboard.allowed_roles.join(", ") || "عمومی"}
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-sky-100">
                  <p className="text-xs text-sky-500">
                    ایجاد شده: {new Date(dashboard.created_at).toLocaleDateString('fa-IR')}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default DashboardListPage;