import { useAuth } from "@/contexts/AuthContext";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const SignupForm: React.FC = () => {
  const [formData, setFormData] = useState({
    hoten: "",
    sodienthoai: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const { hoten, sodienthoai, email, password, confirmPassword } = formData;

    // Simple validation
    if (!hoten || !sodienthoai || !password) {
      setError("Vui lòng điền đầy đủ thông tin bắt buộc");
      return;
    }

    if (password !== confirmPassword) {
      setError("Mật khẩu không khớp");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      await signup({
        hoten,
        sodienthoai,
        password,
        email: email || undefined,
      });

      setSuccess(true);

      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.sodienthoai ||
        err.response?.data?.non_field_errors ||
        "Đã xảy ra lỗi. Vui lòng thử lại.";
      setError(Array.isArray(errorMessage) ? errorMessage[0] : errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-8">
        <div
          className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4"
          role="alert"
        >
          <p>Đăng ký thành công! Đang chuyển hướng đến trang đăng nhập...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-8">
      <h2 className="text-2xl font-semibold mb-6 text-center">
        Đăng ký tài khoản
      </h2>

      {error && (
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
          role="alert"
        >
          <p>{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="hoten" className="block mb-2 text-sm font-medium">
            Họ tên <span className="text-red-600">*</span>
          </label>
          <input
            type="text"
            id="hoten"
            name="hoten"
            value={formData.hoten}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <div className="mb-4">
          <label
            htmlFor="sodienthoai"
            className="block mb-2 text-sm font-medium"
          >
            Số điện thoại <span className="text-red-600">*</span>
          </label>
          <input
            type="tel"
            id="sodienthoai"
            name="sodienthoai"
            value={formData.sodienthoai}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <div className="mb-4">
          <label htmlFor="email" className="block mb-2 text-sm font-medium">
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="mb-4">
          <label htmlFor="password" className="block mb-2 text-sm font-medium">
            Mật khẩu <span className="text-red-600">*</span>
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <div className="mb-6">
          <label
            htmlFor="confirmPassword"
            className="block mb-2 text-sm font-medium"
          >
            Xác nhận mật khẩu <span className="text-red-600">*</span>
          </label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-400"
        >
          {isLoading ? "Đang xử lý..." : "Đăng ký"}
        </button>
      </form>
    </div>
  );
};

export default SignupForm;
