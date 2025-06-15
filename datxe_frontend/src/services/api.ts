import axios from "axios";
import {
  Booking,
  BookingForm,
  LoginForm,
  Shift,
  SignupForm,
  TokenResponse,
  User,
} from "../types";

// Create axios instance
const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Add authorization header interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If unauthorized and not a retry request
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Try to refresh token
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
          // No refresh token, log out
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
          return Promise.reject(error);
        }

        const response = await axios.post("/api/auth/refresh/", {
          refresh: refreshToken,
        });
        const { access } = response.data;

        // Update tokens
        localStorage.setItem("access_token", access);

        // Retry the original request with new token
        originalRequest.headers["Authorization"] = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token invalid, log out
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  signup: (data: SignupForm): Promise<void> =>
    api.post("/auth/signup/", data).then((res) => res.data),

  login: (data: LoginForm): Promise<TokenResponse> =>
    api.post("/auth/login/", data).then((res) => res.data),

  logout: (refreshToken: string): Promise<void> =>
    api
      .post("/auth/logout/", { refresh: refreshToken })
      .then((res) => res.data),
};

// User API calls
export const userAPI = {
  getProfile: (): Promise<User> =>
    api.get("/user/profile/").then((res) => res.data),

  updateProfile: (data: Partial<User>): Promise<User> =>
    api.patch("/user/1/", data).then((res) => res.data), // Using ID 1 as it's always the current user
};

// Booking API calls
export const bookingAPI = {
  getBookings: (): Promise<Booking[]> =>
    api.get("/booking/").then((res) => res.data),

  getBooking: (id: number): Promise<Booking> =>
    api.get(`/booking/${id}/`).then((res) => res.data),

  createBooking: (data: BookingForm): Promise<Booking> =>
    api.post("/booking/", data).then((res) => res.data),

  updateBooking: (id: number, data: Partial<BookingForm>): Promise<Booking> =>
    api.patch(`/booking/${id}/`, data).then((res) => res.data),

  deleteBooking: (id: number): Promise<void> =>
    api.delete(`/booking/${id}/`).then((res) => res.data),
};

// Shift API calls
export const shiftAPI = {
  getShifts: (): Promise<Shift[]> => api.get("/shift/").then((res) => res.data),

  getShift: (id: number): Promise<Shift> =>
    api.get(`/shift/${id}/`).then((res) => res.data),

  createShift: (data: Omit<Shift, "maca">): Promise<Shift> =>
    api.post("/shift/", data).then((res) => res.data),

  updateShift: (id: number, data: Partial<Shift>): Promise<Shift> =>
    api.patch(`/shift/${id}/`, data).then((res) => res.data),

  deleteShift: (id: number): Promise<void> =>
    api.delete(`/shift/${id}/`).then((res) => res.data),
};

export default api;

import { authAPI, bookingAPI, shiftAPI, userAPI } from "@/api/backend";

// Re-export all the API services for easier imports
export { authAPI, bookingAPI, shiftAPI, userAPI };
