import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { LayoutProvider, AuthProvider } from "./contexts";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import DashboardListPage from "./pages/DashboardListPage";
import DashboardViewPage from "./pages/DashboardViewPage";
import BusherUIPage from "./pages/BusherUIPage";
import Layout from "./components/Layout";
import PrivateRoute from "./components/PrivateRoute";
import "./App.css";

function App() {
  return (
    <Router>
      <AuthProvider>
        <LayoutProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            
            {/* Protected routes */}
            <Route path="/" element={
              <PrivateRoute>
                <Layout>
                  <HomePage />
                </Layout>
              </PrivateRoute>
            } />
            <Route path="/dashboards" element={
              <PrivateRoute>
                <Layout>
                  <DashboardListPage />
                </Layout>
              </PrivateRoute>
            } />
            <Route path="/dashboard/:dashboardUuid" element={
              <PrivateRoute>
                <Layout>
                  <DashboardViewPage />
                </Layout>
              </PrivateRoute>
            } />
            <Route path="/busher" element={
              <PrivateRoute>
                <Layout>
                  <BusherUIPage />
                </Layout>
              </PrivateRoute>
            } />
            
            {/* Default route - redirect to login */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </LayoutProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
