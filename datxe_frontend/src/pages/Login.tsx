import React, { useState } from "react";
import {
  Form,
  Input,
  Button,
  Typography,
  Card,
  Alert,
  Spin,
  Divider,
} from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useAuth } from "@/contexts/AuthContext";
import { Link, useNavigate, useLocation } from "react-router-dom";

const { Title, Text } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Get the redirect path from state or default to homepage
  const from = (location.state as any)?.from?.pathname || "/";

  const onFinish = async (values: { username: string; password: string }) => {
    try {
      setLoading(true);
      setError(null);
      await login(values.username, values.password);
      navigate(from, { replace: true });
    } catch (err: any) {
      console.error("Login error:", err);
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.response?.data?.details) {
        setError(JSON.stringify(err.response.data.details));
      } else {
        setError("Đăng nhập thất bại. Vui lòng kiểm tra thông tin đăng nhập.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "40px auto", padding: "0 16px" }}>
      <Card bordered={false} style={{ boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <Title level={2} style={{ textAlign: "center", marginBottom: 24 }}>
          Đăng nhập
        </Title>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}

        <Form
          name="login_form"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: "Vui lòng nhập số điện thoại!" },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              size="large"
              placeholder="Số điện thoại"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: "Vui lòng nhập mật khẩu!" }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              size="large"
              placeholder="Mật khẩu"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              loading={loading}
            >
              Đăng nhập
            </Button>
          </Form.Item>
        </Form>

        <Divider plain>
          <Text type="secondary">Hoặc</Text>
        </Divider>

        <div style={{ textAlign: "center" }}>
          <Text>Chưa có tài khoản? </Text>
          <Link to="/register">Đăng ký ngay</Link>
        </div>
      </Card>

      <Card style={{ marginTop: 16, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <Title level={5}>Tài khoản mẫu:</Title>
        <div style={{ marginBottom: 8 }}>
          <Text strong>Admin:</Text> admin / admin123
        </div>
        <div style={{ marginBottom: 8 }}>
          <Text strong>Tài xế:</Text> 0977000001 / txpass1
        </div>
        <div style={{ marginBottom: 8 }}>
          <Text strong>Nhân viên:</Text> 0909090909 / mypassword789
        </div>
        <div>
          <Text strong>Hành khách:</Text> 0912345678 / password123
        </div>
      </Card>
    </div>
  );
};

export default Login;
