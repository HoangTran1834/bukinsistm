import React, { useState } from 'react';
import { login } from '../api/backend';

export default function LoginForm({ onLogin }: { onLogin: (token: string) => void }) {
  const [form, setForm] = useState({ sodienthoai: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await login(form);
      console.log('Login response:', res);
      if (res && res.access) {
        onLogin(res.access);
      } else {
        setError(res?.detail || 'Đăng nhập thất bại');
      }
    } catch (err) {
      setError('Lỗi kết nối tới server');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Đăng nhập</h2>
      <input name="sodienthoai" placeholder="Số điện thoại" value={form.sodienthoai} onChange={handleChange} required />
      <input name="password" type="password" placeholder="Mật khẩu" value={form.password} onChange={handleChange} required />
      <button type="submit" disabled={loading}>{loading ? 'Đang đăng nhập...' : 'Đăng nhập'}</button>
      {error && <div style={{color:'red'}}>{error}</div>}
    </form>
  );
}
