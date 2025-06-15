import { useAuth } from "@/contexts/AuthContext";
import React, { useState } from "react";
import { Link } from "react-router-dom";

const Navbar: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => setIsMenuOpen((prev) => !prev);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link to="/" className="text-xl font-bold">
              Đặt Xe
            </Link>

            {isAuthenticated && (
              <>
                <Link to="/bookings" className="hover:text-blue-200">
                  Đặt chỗ
                </Link>

                {(user?.vaitro === 0 || user?.vaitro === 2) && (
                  <Link to="/shifts" className="hover:text-blue-200">
                    Ca làm việc
                  </Link>
                )}

                {user?.vaitro === 1 && (
                  <Link to="/driver" className="hover:text-blue-200">
                    Lịch trình
                  </Link>
                )}

                {user?.vaitro === 0 && (
                  <Link to="/admin" className="hover:text-blue-200">
                    Quản trị
                  </Link>
                )}
              </>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/profile" className="hover:text-blue-200">
                  {user?.hoten || "Tài khoản"}
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded"
                >
                  Đăng xuất
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:text-blue-200">
                  Đăng nhập
                </Link>
                <Link
                  to="/signup"
                  className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded"
                >
                  Đăng ký
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
export default Navbar;
