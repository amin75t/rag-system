import React from "react";
import { useLayoutContext } from "../contexts";


export default function HomePage() {
  const { isSidebarOpen, toggleSidebar } = useLayoutContext();

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-sky-100 to-sky-200 p-8 font-iransans" dir="rtl">
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
      <div className="text-center">
        <h1 className="text-5xl font-bold text-sky-900 mb-4 drop-shadow-md">داشبورد جامع RAG System</h1>
        <p className="text-xl text-sky-700 max-w-2xl mx-auto">سیستم مدیریت و نمایش اطلاعات هوشمند</p>
        
        <div className="mt-12 bg-white/80 backdrop-blur-md rounded-xl p-8 max-w-2xl mx-auto shadow-xl border border-sky-200">
          <h2 className="text-2xl font-semibold text-sky-800 mb-4">به داشبورد جامع خوش آمدید</h2>
          <p className="text-sky-600 leading-relaxed">
            از منوی سمت راست برای دسترسی به بخش‌های مختلف سیستم استفاده کنید. شما می‌توانید به داشبوردهای Superset و داشبورد بوشهر دسترسی داشته باشید.
          </p>
        </div>
      </div>
    </div>
  );
}