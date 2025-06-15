import { useAuth } from "@/contexts/AuthContext";
import { bookingAPI } from "@/services/api";
import { Booking } from "@/types";
import React, { useEffect, useState } from "react";

const BookingList: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const { isAdmin, isStaff } = useAuth();

  useEffect(() => {
    const fetchBookings = async () => {
      setIsLoading(true);
      try {
        const data = await bookingAPI.getAll();
        setBookings(data);
        setError("");
      } catch (err) {
        console.error("Error fetching bookings:", err);
        setError("Không thể tải danh sách đặt xe. Vui lòng thử lại sau.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchBookings();
  }, []);

  const getBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "chờ xác nhận":
        return "bg-yellow-100 text-yellow-800";
      case "đã xác nhận":
        return "bg-blue-100 text-blue-800";
      case "đã hoàn thành":
        return "bg-green-100 text-green-800";
      case "đã hủy":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString("vi-VN");
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
        role="alert"
      >
        <p>{error}</p>
      </div>
    );
  }

  if (bookings.length === 0) {
    return (
      <div className="text-center py-8">
        <h3 className="text-lg font-medium text-gray-700">
          Không có đơn đặt xe nào
        </h3>
        <p className="mt-2 text-gray-500">
          Bạn chưa có lịch sử đặt xe nào. Tạo đơn đặt xe mới ngay!
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Mã đặt xe
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Thời gian đặt
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Trạng thái
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Từ
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Đến
            </th>
            {(isAdmin || isStaff) && (
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Người đặt
              </th>
            )}
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Thao tác
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {bookings.map((booking) => (
            <tr key={booking.madatxe}>
              <td className="px-6 py-4 whitespace-nowrap">
                #{booking.madatxe}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {formatDateTime(booking.thoigiandat)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getBadgeColor(
                    booking.trangthai
                  )}`}
                >
                  {booking.trangthai}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">{booking.diemdon}</td>
              <td className="px-6 py-4 whitespace-nowrap">{booking.diemtra}</td>
              {(isAdmin || isStaff) && (
                <td className="px-6 py-4 whitespace-nowrap">
                  ID: {booking.manguoidung}
                </td>
              )}
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  className="text-blue-600 hover:text-blue-900 mr-3"
                  onClick={() => {
                    // View details functionality
                  }}
                >
                  Chi tiết
                </button>
                {booking.trangthai === "Chờ xác nhận" && (
                  <button
                    className="text-red-600 hover:text-red-900"
                    onClick={() => {
                      // Cancel booking functionality
                    }}
                  >
                    Hủy
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BookingList;
