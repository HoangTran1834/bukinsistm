import { useAuth } from "@/contexts/AuthContext";
import { userAPI } from "@/services/api";
import { User } from "@/types";
import React, { useEffect, useState } from "react";

const Profile: React.FC = () => {
  const { user: authUser, isLoading: authLoading } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    hoten: "",
    email: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (authUser) {
      setUser(authUser);
      setFormData({
        hoten: authUser.hoten || "",
        email: authUser.email || "",
      });
    }
  }, [authUser]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!user) return;

    setIsLoading(true);
    setError("");
    setSuccess("");

    try {
      const updatedUser = await userAPI.updateProfile({
        manguoidung: user.manguoidung,
        hoten: formData.hoten,
        email: formData.email || undefined,
      });

      setUser(updatedUser);
      setSuccess("Cập nhật thông tin thành công!");
      setIsEditing(false);
    } catch (err) {
      console.error("Error updating profile:", err);
      setError("Có lỗi xảy ra khi cập nhật thông tin");
    } finally {
      setIsLoading(false);
    }
  };

  if (authLoading) {
    return <div className="text-center py-4">Đang tải...</div>;
  }

  if (!user) {
    return (
      <div className="text-center py-4">
        Không tìm thấy thông tin người dùng
      </div>
    );
  }

  const renderRoleName = () => {
    switch (user.vaitro) {
      case 0:
        return "Quản trị viên";
      case 1:
        return "Tài xế";
      case 2:
        return "Nhân viên";
      case 3:
        return "Hành khách";
      default:
        return "Không xác định";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Thông tin tài khoản</h2>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Chỉnh sửa
          </button>
        )}
      </div>

      {error && (
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
          role="alert"
        >
          <p>{error}</p>
        </div>
      )}

      {success && (
        <div
          className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4"
          role="alert"
        >
          <p>{success}</p>
        </div>
      )}

      {isEditing ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="hoten" className="block mb-1 font-medium">
              Họ tên
            </label>
            <input
              type="text"
              id="hoten"
              name="hoten"
              value={formData.hoten}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>

          <div>
            <label htmlFor="email" className="block mb-1 font-medium">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:bg-blue-400"
            >
              {isLoading ? "Đang lưu..." : "Lưu thay đổi"}
            </button>

            <button
              type="button"
              onClick={() => {
                setIsEditing(false);
                setFormData({
                  hoten: user.hoten || "",
                  email: user.email || "",
                });
              }}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded"
            >
              Hủy
            </button>
          </div>
        </form>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Họ tên</h3>
              <p className="mt-1">{user.hoten}</p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500">
                Số điện thoại
              </h3>
              <p className="mt-1">{user.sodienthoai}</p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500">Email</h3>
              <p className="mt-1">{user.email || "Chưa cung cấp"}</p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500">Vai trò</h3>
              <p className="mt-1">{renderRoleName()}</p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-500">
                Ngày tạo tài khoản
              </h3>
              <p className="mt-1">
                {new Date(user.date_joined).toLocaleDateString("vi-VN")}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
