import React, { useEffect, useState } from 'react';
import { getProfile } from '../api/backend';

export default function Profile({ token }: { token: string }) {
  const [profile, setProfile] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getProfile(token).then(res => {
      if (res && res.sodienthoai) setProfile(res);
      else setError('Không lấy được thông tin');
    });
  }, [token]);

  if (error) return <div style={{color:'red'}}>{error}</div>;
  if (!profile) return <div>Đang tải...</div>;
  return (
    <div>
      <h2>Thông tin cá nhân</h2>
      <div>Họ tên: {profile.hoten}</div>
      <div>SĐT: {profile.sodienthoai}</div>
      <div>Email: {profile.email}</div>
      <div>Vai trò: {profile.vaitro?.tenvaitro || profile.vaitro}</div>
    </div>
  );
}
