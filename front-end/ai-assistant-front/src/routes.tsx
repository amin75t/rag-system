import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import DashboardListPage from "./pages/DashboardListPage";
import DashboardViewPage from "./pages/DashboardViewPage";
import BusherUIPage from "./pages/BusherUIPage";
import ProfilePage from "./pages/ProfilePage";
import ChatPage from "./pages/ChatPage";
import Layout from "./components/Layout";
import PrivateRoute from "./components/PrivateRoute";

const AppRoutes: React.FC = () => {
  return (
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
      <Route path="/chat" element={
        <PrivateRoute>
          <Layout>
            <ChatPage />
          </Layout>
        </PrivateRoute>
      } />
      <Route path="/profile" element={
        <PrivateRoute>
          <Layout>
            <ProfilePage />
          </Layout>
        </PrivateRoute>
      } />
      
      {/* Default route - redirect to login */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default AppRoutes;