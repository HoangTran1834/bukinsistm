import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '@/components/Layout';
import LoginForm from '@/components/LoginForm';

const Login: React.FC = () => {
  return (
    <Layout>
      <div className="max-w-md mx-auto py-8">
        <LoginForm />
        
        <div className="text-center mt-6">
          <p className="text-sm text-gray-600">
            Chưa có tài khoản? {' '}
            <Link to="/signup" className="text-blue-600 hover:underline">
              Đăng ký tại đây
            </Link>
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default Login;
      <div className="auth-card">
        <h2>Đăng nhập</h2>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
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
            {loading ? 'Đang xử lý...' : 'Đăng nhập'}
          </button>
        </form>
        
        <div className="auth-links">
          <p>
            Chưa có tài khoản? <Link to="/signup">Đăng ký</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
