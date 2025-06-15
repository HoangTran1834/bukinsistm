import { useAuth } from "@/contexts/AuthContext";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginForm: React.FC = () => {
  const [sodienthoai, setSodienthoai] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!sodienthoai || !password) {
      setError("Vui lòng nhập số điện thoại và mật khẩu");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      await login({ sodienthoai, password });
      navigate("/");
    } catch (err) {
      setError(
        "Sai thông tin đăng nhập. Vui lòng kiểm tra lại số điện thoại và mật khẩu."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-8">
      <h2 className="text-2xl font-semibold mb-6 text-center">Đăng nhập</h2>

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
          <label
            htmlFor="sodienthoai"
            className="block mb-2 text-sm font-medium"
          >
            Số điện thoại
          </label>
          <input
            type="text"
            id="sodienthoai"
            value={sodienthoai}
            onChange={(e) => setSodienthoai(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <div className="mb-6">
          <label htmlFor="password" className="block mb-2 text-sm font-medium">
            Mật khẩu
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-400"
        >
          {isLoading ? "Đang xử lý..." : "Đăng nhập"}
        </button>
      </form>
    </div>
  );
};

export default LoginForm;
