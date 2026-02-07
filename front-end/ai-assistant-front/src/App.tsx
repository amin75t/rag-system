import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { LayoutProvider, AuthProvider } from "./contexts";
import AppRoutes from "./routes";
import "./App.css";

function App() {
  return (
    <Router>
      <AuthProvider>
        <LayoutProvider>
          <AppRoutes />
        </LayoutProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
