import {
  AuthTokens,
  Booking,
  LoginCredentials,
  Shift,
  SignupData,
  User,
} from "@/types";
import axios from "axios";

const API_URL = "/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh on 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
          throw new Error("No refresh token available");
        }

        const response = await axios.post(`${API_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        localStorage.setItem("access_token", response.data.access);

        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, logout the user
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response = await api.post<AuthTokens>("/auth/login/", credentials);
    return response.data;
  },

  signup: async (userData: SignupData): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>(
      "/auth/signup/",
      userData
    );
    return response.data;
  },

  logout: async (refreshToken: string): Promise<void> => {
    await api.post("/auth/logout/", { refresh: refreshToken });
  },
};

// User API
export const userAPI = {
  getProfile: async (): Promise<User> => {
    const response = await api.get<User>("/user/profile/");
    return response.data;
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await api.patch<User>(
      `/user/${userData.manguoidung}/`,
      userData
    );
    return response.data;
  },
};

// Booking API
export const bookingAPI = {
  getAll: async (): Promise<Booking[]> => {
    const response = await api.get<Booking[]>("/booking/");
    return response.data;
  },

  getById: async (id: number): Promise<Booking> => {
    const response = await api.get<Booking>(`/booking/${id}/`);
    return response.data;
  },

  create: async (bookingData: Partial<Booking>): Promise<Booking> => {
    const response = await api.post<Booking>("/booking/", bookingData);
    return response.data;
  },

  update: async (
    id: number,
    bookingData: Partial<Booking>
  ): Promise<Booking> => {
    const response = await api.patch<Booking>(`/booking/${id}/`, bookingData);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/booking/${id}/`);
  },
};

// Shift API
export const shiftAPI = {
  getAll: async (): Promise<Shift[]> => {
    const response = await api.get<Shift[]>("/shift/");
    return response.data;
  },

  getById: async (id: number): Promise<Shift> => {
    const response = await api.get<Shift>(`/shift/${id}/`);
    return response.data;
  },

  create: async (shiftData: Partial<Shift>): Promise<Shift> => {
    const response = await api.post<Shift>("/shift/", shiftData);
    return response.data;
  },

  update: async (id: number, shiftData: Partial<Shift>): Promise<Shift> => {
    const response = await api.patch<Shift>(`/shift/${id}/`, shiftData);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/shift/${id}/`);
  },
};

export default api;
