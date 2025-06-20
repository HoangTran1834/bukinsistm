import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/authContext";

// Protected route component
export const ProtectedRoute = ({ children }: { children: React.ReactElement }) => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Admin only route component
export const AdminRoute = ({ children }: { children: React.ReactElement }) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.vaitro !== "Admin") {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};
