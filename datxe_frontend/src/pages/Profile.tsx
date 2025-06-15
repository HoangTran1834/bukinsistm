import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import "./Profile.css";

const Profile = () => {
  const { user, updateProfile, loading, error } = useAuth();

  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    hoten: user?.hoten || "",
    email: user?.email || "",
    sodienthoai: user?.sodienthoai || "",
  });

  const [successMessage, setSuccessMessage] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await updateProfile(formData);
      setIsEditing(false);
      setSuccessMessage("Thông tin đã được cập nhật thành công");

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage("");
      }, 3000);
    } catch (err) {
      console.error(err);
    }
  };

  const getRoleName = (roleId: number): string => {
    switch (roleId) {
      case 0:
        return "Admin";
      case 1:
        return "Tài xế";
      case 2:
        return "Nhân viên";
      case 3:
        return "Khách hàng";
      default:
        return "Không xác định";
    }
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h1>Thông tin cá nhân</h1>
        {!isEditing && (
          <button
            className="profile-edit-button"
            onClick={() => setIsEditing(true)}
          >
            Chỉnh sửa
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
      {successMessage && (
        <div className="success-message">{successMessage}</div>
      )}

      {isEditing ? (
        <form className="profile-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="hoten">Họ và tên</label>
            <input
              type="text"
              id="hoten"
              name="hoten"
              value={formData.hoten}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="sodienthoai">Số điện thoại</label>
            <input
              type="text"
              id="sodienthoai"
              name="sodienthoai"
              value={formData.sodienthoai}
              onChange={handleChange}
              readOnly
            />
            <small>Không thể thay đổi số điện thoại</small>
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email || ""}
              onChange={handleChange}
            />
          </div>

          <div className="profile-form-buttons">
            <button
              type="button"
              className="cancel-button"
              onClick={() => setIsEditing(false)}
            >
              Hủy
            </button>
            <button type="submit" className="save-button" disabled={loading}>
              {loading ? "Đang lưu..." : "Lưu thay đổi"}
            </button>
          </div>
        </form>
      ) : (
        <div className="profile-info">
          <div className="info-group">
            <span className="info-label">Họ và tên:</span>
            <span className="info-value">{user.hoten}</span>
          </div>

          <div className="info-group">
            <span className="info-label">Số điện thoại:</span>
            <span className="info-value">{user.sodienthoai}</span>
          </div>

          <div className="info-group">
            <span className="info-label">Email:</span>
            <span className="info-value">{user.email || "Chưa cập nhật"}</span>
          </div>

          <div className="info-group">
            <span className="info-label">Vai trò:</span>
            <span className="info-value">{getRoleName(user.vaitro)}</span>
          </div>

          <div className="info-group">
            <span className="info-label">Ngày tham gia:</span>
            <span className="info-value">
              {new Date(user.date_joined).toLocaleDateString("vi-VN")}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
