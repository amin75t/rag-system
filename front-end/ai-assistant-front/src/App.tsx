import React from "react";
import DashboardList from "./components/DashboardList";
import "./App.css";

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Superset Dashboard Embedding</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Available Dashboards</h2>
            <p className="text-gray-600">Select a dashboard to view it embedded via Superset Guest Token.</p>
          </div>

          {/* DashboardList handles selection + embedded view internally */}
          <DashboardList />
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">Powered by Apache Superset & React</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
