import axios, { AxiosRequestConfig } from "axios";

// Lấy API URL từ biến môi trường hoặc sử dụng URL mặc định
const apiUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const instance = axios.create({
  baseURL: `${apiUrl}/api`,
  timeout: 30000,
});

// Request interceptor để thêm token vào header
instance.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const token = localStorage.getItem("access_token");
    if (token && config.headers) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor để xử lý lỗi chung
instance.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Nếu lỗi 401 (Unauthorized) và chưa thử refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Thử refresh token
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
          // Không có refresh token, chuyển đến trang login
          window.location.href = "/login";
          return Promise.reject(error);
        }

        const response = await axios.post(`${apiUrl}/api/auth/refresh/`, {
          refresh: refreshToken,
        });

        if (response.data.access) {
          localStorage.setItem("access_token", response.data.access);

          // Cập nhật token trong header của request ban đầu
          originalRequest.headers["Authorization"] = `Bearer ${response.data.access}`;
          return instance(originalRequest);
        }
      } catch (refreshError) {
        // Refresh token không thành công, logout
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default instance;
