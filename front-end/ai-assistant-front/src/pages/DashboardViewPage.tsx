import React from "react";
import { useParams, Link } from "react-router-dom";
import SupersetDashboard from "../components/SupersetDashboard";

const DashboardViewPage: React.FC = () => {
  const { dashboardUuid } = useParams<{ dashboardUuid: string }>();

  if (!dashboardUuid) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200">
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
          <p className="text-red-600 font-medium mb-2">خطا</p>
          <p className="text-sky-600 text-sm">UUID داشبورد ارائه نشده است</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 min-h-screen" dir="rtl">
      <div className="mb-6">
        <Link
          to="/dashboards"
          className="inline-flex items-center text-sky-600 hover:text-sky-800 transition-colors"
        >
          <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          بازگشت به لیست داشبوردها
        </Link>
      </div>

      <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-md p-6 border border-sky-200">
        <h2 className="text-2xl font-bold mb-4 text-sky-900">نمایش داشبورد</h2>
        <SupersetDashboard
          dashboardUuid={dashboardUuid}
          onDashboardLoad={() => console.log("Dashboard loaded successfully")}
          onDashboardError={(errMsg) => console.error("Dashboard error:", errMsg)}
        />
      </div>
    </div>
  );
};

export default DashboardViewPage;