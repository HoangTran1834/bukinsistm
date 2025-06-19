import React, { JSX } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Layout, ConfigProvider } from "antd";
import viVN from "antd/lib/locale/vi_VN";
import { AuthProvider, useAuth } from "./contexts/authContext";
import Navbar from "./components/Layout/Navbar";
import Footer from "./components/Layout/Footer";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import NotFound from "./pages/NotFound";
import "./App.css";

const { Content } = Layout;

// Protected route component
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Admin only route component
const AdminRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.vaitro !== "Admin") {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

// Main App component for routing
const AppRoutes: React.FC = () => {
  return (
    <Router>
      <Layout style={{ minHeight: "100vh" }}>
        <Navbar />
        <Content style={{ padding: "0 0 24px 0", flex: 1 }}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Add more routes here as needed */}

            {/* Protected routes - require authentication */}
            {/* <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } /> */}

            {/* Admin only routes */}
            {/* <Route path="/admin" element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            } /> */}

            {/* 404 route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Content>
        <Footer />
      </Layout>
    </Router>
  );
};

// Root App component with providers
const App: React.FC = () => {
  return (
    <ConfigProvider locale={viVN}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ConfigProvider>
  );
};

export default App;
