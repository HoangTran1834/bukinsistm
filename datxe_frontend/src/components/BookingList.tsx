import React, { useEffect, useState } from 'react';
import { getBookings } from '../api/backend';

export default function BookingList({ token }: { token: string }) {
  const [bookings, setBookings] = useState<any[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    getBookings(token).then(res => {
      if (Array.isArray(res)) setBookings(res);
      else setError('Không lấy được danh sách đặt xe');
    });
  }, [token]);

  if (error) return <div style={{color:'red'}}>{error}</div>;
  return (
    <div>
      <h2>Danh sách đặt xe</h2>
      <ul>
        {bookings.map((b, i) => (
          <li key={i}>
            Mã: {b.madatxe} | Trạng thái: {b.trangthai} | Điểm đón: {b.diemdon?.tendiadiem || b.diemdon} | Điểm trả: {b.diemtra?.tendiadiem || b.diemtra}
          </li>
        ))}
      </ul>
    </div>
  );
}
