import React, { useState } from "react";
import { Form, Input, Button, Typography, Card, Alert, Divider } from "antd";
import {
  UserOutlined,
  LockOutlined,
  PhoneOutlined,
  MailOutlined,
} from "@ant-design/icons";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/authContext";
import { notification } from "antd";
import { registerUserAPI } from "../services/api.service";

const { Title, Text } = Typography;

const Register: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { register } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: {
    fullName: string;
    phone: string;
    password: string;
    confirmPassword: string;
    email?: string;
  }) => {
    if (values.password !== values.confirmPassword) {
      setError("Mật khẩu xác nhận không khớp!");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await registerUserAPI(
        values.fullName,
        values.phone,
        values.password,
        values.email ?? ""
      );

      if (res.data) {
        notification.success({
          message: "Đăng ký",
          description: "Đăng ký thành công!",
        });
        navigate("/");
      } else {
        notification.error({
          message: "Đăng ký",
          description:
            Array.isArray(res?.data?.message) || typeof res?.data?.message === "string"
              ? res?.data?.message
              : "Đăng ký thất bại. Vui lòng thử lại sau.",
        });
      }
    } catch (err: any) {
      console.error("Registration error:", err);
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.response?.data?.details) {
        setError(JSON.stringify(err.response.data.details));
      } else {
        setError("Đăng ký thất bại. Vui lòng thử lại sau.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "40px auto", padding: "0 16px" }}>
      <Card bordered={false} style={{ boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
        <Title level={2} style={{ textAlign: "center", marginBottom: 24 }}>
          Đăng ký tài khoản
        </Title>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}

        <Form name="register_form" onFinish={onFinish} layout="vertical">
          <Form.Item
            name="fullName"
            rules={[{ required: true, message: "Vui lòng nhập họ tên!" }]}
          >
            <Input
              prefix={<UserOutlined />}
              size="large"
              placeholder="Họ và tên"
            />
          </Form.Item>

          <Form.Item
            name="phone"
            rules={[
              { required: true, message: "Vui lòng nhập số điện thoại!" },
              {
                pattern: /^[0-9]{10,11}$/,
                message: "Số điện thoại không hợp lệ!",
              },
            ]}
          >
            <Input
              prefix={<PhoneOutlined />}
              size="large"
              placeholder="Số điện thoại"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[{ type: "email", message: "Email không hợp lệ!" }]}
          >
            <Input
              prefix={<MailOutlined />}
              size="large"
              placeholder="Email (tùy chọn)"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: "Vui lòng nhập mật khẩu!" },
              { min: 6, message: "Mật khẩu phải có ít nhất 6 ký tự!" },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              size="large"
              placeholder="Mật khẩu"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            rules={[{ required: true, message: "Vui lòng xác nhận mật khẩu!" }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              size="large"
              placeholder="Xác nhận mật khẩu"
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
              Đăng ký
            </Button>
          </Form.Item>
        </Form>

        <Divider plain>
          <Text type="secondary">Hoặc</Text>
        </Divider>

        <div style={{ textAlign: "center" }}>
          <Text>Đã có tài khoản? </Text>
          <Link to="/login">Đăng nhập</Link>
        </div>
      </Card>
    </div>
  );
};

export default Register;
