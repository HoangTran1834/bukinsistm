import Layout from "@/components/Layout";
import { useAuth } from "@/contexts/AuthContext";
import React from "react";
import { Link } from "react-router-dom";

const Home: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="bg-blue-600 text-white rounded-lg p-8 md:p-12 mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            Dịch vụ đặt xe an toàn và tiện lợi
          </h1>
          <p className="text-lg md:text-xl mb-6">
            Đặt xe nhanh chóng, theo dõi hành trình và di chuyển thuận tiện cùng
            đội ngũ tài xế chuyên nghiệp
          </p>

          {!isAuthenticated ? (
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                to="/signup"
                className="bg-white text-blue-600 hover:bg-blue-100 px-6 py-2 rounded-md font-medium text-center"
              >
                Đăng ký ngay
              </Link>
              <Link
                to="/login"
                className="border-2 border-white text-white hover:bg-white hover:text-blue-600 px-6 py-2 rounded-md font-medium text-center"
              >
                Đăng nhập
              </Link>
            </div>
          ) : (
            <Link
              to="/bookings"
              className="bg-white text-blue-600 hover:bg-blue-100 px-6 py-2 rounded-md font-medium inline-block"
            >
              Đặt xe ngay
            </Link>
          )}
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-blue-600 text-4xl mb-4">🚖</div>
            <h3 className="text-xl font-semibold mb-2">Đặt xe dễ dàng</h3>
            <p className="text-gray-600">
              Đặt xe chỉ với vài thao tác đơn giản, tiết kiệm thời gian và công
              sức.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-blue-600 text-4xl mb-4">🛣️</div>
            <h3 className="text-xl font-semibold mb-2">Nhiều lộ trình</h3>
            <p className="text-gray-600">
              Đa dạng lựa chọn tuyến đường với giá cả hợp lý cho mọi nhu cầu di
              chuyển.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-blue-600 text-4xl mb-4">👨‍✈️</div>
            <h3 className="text-xl font-semibold mb-2">Tài xế chuyên nghiệp</h3>
            <p className="text-gray-600">
              Đội ngũ tài xế được đào tạo bài bản, nhiệt tình và chu đáo với
              hành khách.
            </p>
          </div>
        </div>

        {/* User-specific Section */}
        {isAuthenticated && (
          <div className="bg-gray-50 rounded-lg p-8 mb-12">
            <h2 className="text-2xl font-semibold mb-4">
              Xin chào {user?.hoten || "Quý khách"}!
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Link
                to="/bookings"
                className="bg-white p-4 rounded-md shadow hover:shadow-md transition-shadow border-l-4 border-blue-500"
              >
                <h3 className="font-medium mb-1">Đặt xe</h3>
                <p className="text-sm text-gray-600">Tạo đơn đặt xe mới</p>
              </Link>

              <Link
                to="/profile"
                className="bg-white p-4 rounded-md shadow hover:shadow-md transition-shadow border-l-4 border-green-500"
              >
                <h3 className="font-medium mb-1">Tài khoản</h3>
                <p className="text-sm text-gray-600">
                  Quản lý thông tin cá nhân
                </p>
              </Link>

              {(user?.vaitro === 0 || user?.vaitro === 2) && (
                <Link
                  to="/shifts"
                  className="bg-white p-4 rounded-md shadow hover:shadow-md transition-shadow border-l-4 border-purple-500"
                >
                  <h3 className="font-medium mb-1">Ca làm việc</h3>
                  <p className="text-sm text-gray-600">Quản lý ca tài xế</p>
                </Link>
              )}

              {user?.vaitro === 0 && (
                <Link
                  to="/admin"
                  className="bg-white p-4 rounded-md shadow hover:shadow-md transition-shadow border-l-4 border-red-500"
                >
                  <h3 className="font-medium mb-1">Quản trị</h3>
                  <p className="text-sm text-gray-600">Quản lý hệ thống</p>
                </Link>
              )}
            </div>
          </div>
        )}

        {/* How it Works Section */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold mb-6 text-center">
            Cách thức hoạt động
          </h2>

          <div className="flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="flex flex-col items-center text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center text-blue-600 text-2xl font-bold mb-4">
                1
              </div>
              <h3 className="font-medium mb-2">Đăng ký tài khoản</h3>
              <p className="text-gray-600 text-sm">
                Tạo tài khoản với số điện thoại và mật khẩu
              </p>
            </div>

            <div className="hidden md:block text-gray-300 text-2xl">→</div>

            <div className="flex flex-col items-center text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center text-blue-600 text-2xl font-bold mb-4">
                2
              </div>
              <h3 className="font-medium mb-2">Chọn lộ trình</h3>
              <p className="text-gray-600 text-sm">
                Chọn điểm đón và điểm đến cho chuyến đi của bạn
              </p>
            </div>

            <div className="hidden md:block text-gray-300 text-2xl">→</div>

            <div className="flex flex-col items-center text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center text-blue-600 text-2xl font-bold mb-4">
                3
              </div>
              <h3 className="font-medium mb-2">Đặt lịch</h3>
              <p className="text-gray-600 text-sm">
                Chọn thời gian phù hợp và xác nhận đặt xe
              </p>
            </div>

            <div className="hidden md:block text-gray-300 text-2xl">→</div>

            <div className="flex flex-col items-center text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center text-blue-600 text-2xl font-bold mb-4">
                4
              </div>
              <h3 className="font-medium mb-2">Trải nghiệm hành trình</h3>
              <p className="text-gray-600 text-sm">
                Tài xế đón bạn đúng giờ và đưa bạn đến điểm đến
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Home;
