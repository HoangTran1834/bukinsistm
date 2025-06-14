import React, { useState } from 'react';
import { signup } from '../api/backend';

export default function SignupForm({ onSignup }: { onSignup: () => void }) {
  const [form, setForm] = useState({ hoten: '', sodienthoai: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    const res = await signup(form);
    if (res && res.sodienthoai) {
      setSuccess(true);
      onSignup();
    } else {
      setError(res?.detail || 'Đăng ký thất bại');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Đăng ký</h2>
      <input name="hoten" placeholder="Họ tên" value={form.hoten} onChange={handleChange} required />
      <input name="sodienthoai" placeholder="Số điện thoại" value={form.sodienthoai} onChange={handleChange} required />
      <input name="password" type="password" placeholder="Mật khẩu" value={form.password} onChange={handleChange} required />
      <button type="submit">Đăng ký</button>
      {error && <div style={{color:'red'}}>{error}</div>}
      {success && <div style={{color:'green'}}>Đăng ký thành công!</div>}
    </form>
  );
}
