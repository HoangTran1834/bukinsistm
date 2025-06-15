import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '@/components/Layout';
import SignupForm from '@/components/SignupForm';

const Signup: React.FC = () => {
  return (
    <Layout>
      <div className="max-w-md mx-auto py-8">
        <SignupForm />
        
        <div className="text-center mt-6">
          <p className="text-sm text-gray-600">
            Đã có tài khoản? {' '}
            <Link to="/login" className="text-blue-600 hover:underline">
              Đăng nhập
            </Link>
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default Signup;
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Đăng ký tài khoản</h2>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
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
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email (tùy chọn)</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Mật khẩu</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          
          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Đang xử lý...' : 'Đăng ký'}
          </button>
        </form>
        
        <div className="auth-links">
          <p>
            Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;
