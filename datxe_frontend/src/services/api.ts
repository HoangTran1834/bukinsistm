import axios, { type AxiosInstance, type AxiosResponse } from "axios";

// Base URL
const BASE_URL = "http://localhost:8000/api";

// Token management
const getAccessToken = (): string | null =>
  localStorage.getItem("access_token");
const getRefreshToken = (): string | null =>
  localStorage.getItem("refresh_token");
const setTokens = (access: string, refresh: string): void => {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
};
const clearTokens = (): void => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          const response = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = response.data;
          localStorage.setItem("access_token", access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          clearTokens();
          console.error("Token refresh failed:", refreshError);
          window.location.href = "/login";
        }
      } else {
        clearTokens();
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

// Types
interface SignupData {
  hoten: string;
  sodienthoai: string;
  password: string;
  email?: string;
}

interface LoginData {
  sodienthoai: string;
  password: string;
}

interface LoginResponse {
  access: string;
  refresh: string;
  user: any;
}

interface BookingData {
  diemdon: number;
  diemtra: number;
  matuyenduong: number;
  machitietca: number;
  chitietdatxe?: Array<{
    tenkhach: string;
    sodienthoaikhach: string;
    diemdon: number;
    diemtra: number;
    matuyenduong: number;
    trangthai: string;
    machitietca: number;
  }>;
}

interface AutoAssignData {
  tenkhach: string;
  sodienthoaikhach: string;
  huong: number;
  thoigian: string;
}

interface CheckSlotData {
  machitietca: number;
  huong: number;
}

interface GetDirectionData {
  diemdon: number;
  diemtra: number;
}

interface GetDistrictData {
  diemdon: number;
}

interface GetPriceData {
  matuyenduong: number;
}

interface StatisticsData {
  tu_ngay: string;
  den_ngay: string;
}

interface RouteData {
  matuyenduong?: number;
  tentuyenduong: string;
  giatien: number;
}

// Auth API
export const authAPI = {
  // Đăng ký tài khoản mới
  signup: async (data: SignupData): Promise<AxiosResponse> => {
    return await apiClient.post("/auth/signup/", data);
  },

  // Đăng nhập
  login: async (data: LoginData): Promise<LoginResponse> => {
    const response = await apiClient.post("/auth/login/", data);
    const { access, refresh } = response.data;
    setTokens(access, refresh);
    return response.data;
  },

  // Đăng xuất
  logout: async (): Promise<AxiosResponse> => {
    const refreshToken = getRefreshToken();
    const response = await apiClient.post("/auth/logout/", {
      refresh: refreshToken,
    });
    clearTokens();
    return response;
  },

  // Đặt lại mật khẩu
  resetPassword: async (newPassword: string): Promise<AxiosResponse> => {
    return await apiClient.post("/auth/reset_pw/", {
      new_password: newPassword,
    });
  },
};

// User API
export const userAPI = {
  // Lấy danh sách tất cả user
  getUsers: async (): Promise<AxiosResponse> => {
    return await apiClient.get("/user/");
  },

  // Lấy thông tin user theo ID
  getUserById: async (id: number): Promise<AxiosResponse> => {
    return await apiClient.get(`/user/${id}/`);
  },

  // Lấy thông tin profile hiện tại
  getProfile: async (): Promise<AxiosResponse> => {
    return await apiClient.get("/user/profile/");
  },

  // Cập nhật thông tin user
  updateUser: async (id: number, data: any): Promise<AxiosResponse> => {
    return await apiClient.put(`/user/${id}/`, data);
  },

  // Cập nhật một phần thông tin user
  partialUpdateUser: async (id: number, data: any): Promise<AxiosResponse> => {
    return await apiClient.patch(`/user/${id}/`, data);
  },
};

// Shift API
export const shiftAPI = {
  // Lấy danh sách ca
  getShifts: async (): Promise<AxiosResponse> => {
    return await apiClient.get("/shift/");
  },

  // Lấy thông tin ca theo ID
  getShiftById: async (id: number): Promise<AxiosResponse> => {
    return await apiClient.get(`/shift/${id}/`);
  },

  // Tạo ca mới
  createShift: async (data: any): Promise<AxiosResponse> => {
    return await apiClient.post("/shift/", data);
  },

  // Cập nhật ca
  updateShift: async (id: number, data: any): Promise<AxiosResponse> => {
    return await apiClient.put(`/shift/${id}/`, data);
  },

  // Cập nhật một phần ca
  partialUpdateShift: async (id: number, data: any): Promise<AxiosResponse> => {
    return await apiClient.patch(`/shift/${id}/`, data);
  },

  // Xóa ca
  deleteShift: async (id: number): Promise<AxiosResponse> => {
    return await apiClient.delete(`/shift/${id}/`);
  },
};

// Booking API
export const bookingAPI = {
  // Lấy danh sách booking
  getBookings: async (): Promise<AxiosResponse> => {
    return await apiClient.get("/booking/");
  },

  // Lấy thông tin booking theo ID
  getBookingById: async (id: number): Promise<AxiosResponse> => {
    return await apiClient.get(`/booking/${id}/`);
  },

  // Tạo booking mới
  createBooking: async (data: BookingData): Promise<AxiosResponse> => {
    return await apiClient.post("/booking/", data);
  },

  // Cập nhật booking
  updateBooking: async (
    id: number,
    data: BookingData
  ): Promise<AxiosResponse> => {
    return await apiClient.put(`/booking/${id}/`, data);
  },

  // Cập nhật một phần booking
  partialUpdateBooking: async (
    id: number,
    data: Partial<BookingData>
  ): Promise<AxiosResponse> => {
    return await apiClient.patch(`/booking/${id}/`, data);
  },

  // Xóa booking
  deleteBooking: async (id: number): Promise<AxiosResponse> => {
    return await apiClient.delete(`/booking/${id}/`);
  },

  // Tự động xếp hành khách vào chi tiết ca còn chỗ
  autoAssign: async (data: AutoAssignData): Promise<AxiosResponse> => {
    return await apiClient.post("/booking/auto_assign/", data);
  },

  // Kiểm tra số chỗ còn lại trong một chi tiết ca
  checkSlot: async (data: CheckSlotData): Promise<AxiosResponse> => {
    return await apiClient.post("/booking/check_slot/", data);
  },

  // Tính hướng di chuyển giữa hai địa điểm
  getDirection: async (data: GetDirectionData): Promise<AxiosResponse> => {
    return await apiClient.post("/booking/get_direction/", data);
  },

  // Tính huyện của một địa chỉ
  getDistrict: async (data: GetDistrictData): Promise<AxiosResponse> => {
    return await apiClient.post("/booking/get_district/", data);
  },

  // Tính giá dự kiến cho một lộ trình
  getPrice: async (data: GetPriceData): Promise<AxiosResponse> => {
    return await apiClient.post("/booking/get_price/", data);
  },

  // Lấy danh sách các tài xế đang trực
  getDriversOnline: async (): Promise<AxiosResponse> => {
    return await apiClient.get("/booking/drivers_online/");
  },

  // Lấy danh sách các ca tài xế theo ngày
  getShiftsByDate: async (): Promise<AxiosResponse> => {
    return await apiClient.get("/booking/shifts_by_date/");
  },

  // Lấy thống kê số lượng tài xế, hành khách, đặt xe theo thời gian
  getStatistics: async (data: StatisticsData): Promise<AxiosResponse> => {
    return await apiClient.post("/booking/statistics/", data);
  },

  // Lấy danh sách các tuyến đường
  getRoutes: async (): Promise<AxiosResponse> => {
    return await apiClient.get("/booking/routes/");
  },

  // Tạo mới một tuyến đường
  createRoute: async (data: RouteData): Promise<AxiosResponse> => {
    return await apiClient.post("/booking/routes/", data);
  },

  // Cập nhật thông tin một tuyến đường
  updateRoute: async (data: RouteData): Promise<AxiosResponse> => {
    return await apiClient.put("/booking/routes/", data);
  },

  // Xóa một tuyến đường
  deleteRoute: async (matuyenduong: number): Promise<AxiosResponse> => {
    return await apiClient.delete("/booking/routes/", {
      data: { matuyenduong },
    });
  },
};

// Utility functions
export const tokenUtils = {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
  isAuthenticated: (): boolean => !!getAccessToken(),
};

// Export default axios instance for custom requests
export default apiClient;
