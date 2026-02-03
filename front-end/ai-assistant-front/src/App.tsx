import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { LayoutProvider } from "./contexts";
import HomePage from "./pages/HomePage";
import DashboardListPage from "./pages/DashboardListPage";
import DashboardViewPage from "./pages/DashboardViewPage";
import BusherUIPage from "./pages/BusherUIPage";
import Layout from "./components/Layout";
import "./App.css";

function App() {
  return (
    <Router>
      <LayoutProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboards" element={<DashboardListPage />} />
            <Route path="/dashboard/:dashboardUuid" element={<DashboardViewPage />} />
            <Route path="/busher" element={<BusherUIPage />} />
          </Routes>
        </Layout>
      </LayoutProvider>
    </Router>
  );
}

export default App;
