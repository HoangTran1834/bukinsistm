import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import Layout from "./components/Layout";
import { useAuth } from "./contexts/AuthContext";
import BookingCreate from "./pages/BookingCreate";
import BookingDetail from "./pages/BookingDetail";
import BookingList from "./pages/BookingList";
import Home from "./pages/Home";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import Profile from "./pages/Profile";
import ShiftList from "./pages/ShiftList";
import Signup from "./pages/Signup";

function App() {
  const { isAuthenticated, user } = useAuth();

  const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
  };

  const StaffRoute = ({ children }: { children: React.ReactNode }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }

    // Check if user is admin (0) or staff (2)
    if (user?.vaitro !== 0 && user?.vaitro !== 2) {
      return <Navigate to="/" replace />;
    }

    return <>{children}</>;
  };

  const DriverRoute = ({ children }: { children: React.ReactNode }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }

    // Check if user is driver (1)
    if (user?.vaitro !== 1) {
      return <Navigate to="/" replace />;
    }

    return <>{children}</>;
  };

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="signup" element={<Signup />} />

        <Route
          path="profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />

        <Route path="bookings">
          <Route
            index
            element={
              <ProtectedRoute>
                <BookingList />
              </ProtectedRoute>
            }
          />
          <Route
            path="new"
            element={
              <ProtectedRoute>
                <BookingCreate />
              </ProtectedRoute>
            }
          />
          <Route
            path=":id"
            element={
              <ProtectedRoute>
                <BookingDetail />
              </ProtectedRoute>
            }
          />
        </Route>

        <Route
          path="shifts"
          element={
            <StaffRoute>
              <ShiftList />
            </StaffRoute>
          }
        />

        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

export default App;
