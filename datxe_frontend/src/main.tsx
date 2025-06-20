import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./App";
import "./index.css";
import HomePage from "./pages/Home.tsx";
import LoginPage from "./pages/Login.tsx";
import NotFoundPage from "./pages/NotFound.tsx";
import RegisterPage from "./pages/Register.tsx";
import Profile from "./components/Profile.tsx";
import ShiftsManagement from "./pages/ShiftsManagement.tsx";
import Booking from "./pages/Booking.tsx";
import DriverShifts from "./pages/DriverShifts.tsx";
import StaffBooking from "./pages/StaffBooking.tsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <NotFoundPage />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: "login",
        element: <LoginPage />,
      },      {
        path: "register",
        element: <RegisterPage />,
      },      {
        path: "profile",
        element: <Profile />,
      },
      {
        path: "shifts",
        element: <ShiftsManagement />,
      },      {
        path: "booking",
        element: <Booking />,
      },      {
        path: "driver-shifts",
        element: <DriverShifts />,
      },
      {
        path: "staff/booking",
        element: <StaffBooking />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
