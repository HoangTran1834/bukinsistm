import React, { useEffect, useState } from 'react';
import { Card, Avatar, Descriptions, Button, Spin, message, Tag } from 'antd';
import { UserOutlined, EditOutlined, PhoneOutlined, MailOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/authContext';

const Profile: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);

  // Format date để hiển thị
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Không xác định';
    }
  };

  // Lấy màu cho role tag
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'Admin':
        return 'red';
      case 'Tài xế':
        return 'blue';
      case 'Hành khách':
        return 'green';
      default:
        return 'default';
    }
  };

  if (!isAuthenticated || !user) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
        <p>Đang tải thông tin người dùng...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <Card
        title="Thông tin cá nhân"
        extra={<Button icon={<EditOutlined />} type="primary">Chỉnh sửa</Button>}
        loading={loading}
      >
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
          <Avatar size={80} icon={<UserOutlined />} />
          <div style={{ marginLeft: '16px' }}>
            <h3>{user.hoten}</h3>
            <Tag color={getRoleColor(user.vaitro)}>{user.vaitro}</Tag>
            {user.email && (
              <p style={{ margin: '4px 0', color: '#666' }}>
                <MailOutlined /> {user.email}
              </p>
            )}
            <p style={{ margin: '4px 0', color: '#666' }}>
              <PhoneOutlined /> {user.sodienthoai}
            </p>
          </div>
        </div>
        
        <Descriptions bordered column={1}>
          <Descriptions.Item label="Mã người dùng">#{user.manguoidung}</Descriptions.Item>
          <Descriptions.Item label="Họ và tên">{user.hoten}</Descriptions.Item>
          <Descriptions.Item label="Vai trò">
            <Tag color={getRoleColor(user.vaitro)}>{user.vaitro}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Số điện thoại">{user.sodienthoai}</Descriptions.Item>
          <Descriptions.Item label="Email">{user.email || 'Chưa cập nhật'}</Descriptions.Item>
          <Descriptions.Item label="Ngày tham gia">{formatDate(user.date_joined)}</Descriptions.Item>
          <Descriptions.Item label="Lần đăng nhập cuối">
            {user.last_login ? formatDate(user.last_login) : 'Chưa đăng nhập lần nào'}
          </Descriptions.Item>
          <Descriptions.Item label="Trạng thái tài khoản">
            <Tag color={user.is_active ? 'green' : 'red'}>
              {user.is_active ? 'Hoạt động' : 'Bị khóa'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Là nhân viên">
            <Tag color={user.is_staff ? 'blue' : 'default'}>
              {user.is_staff ? 'Là nhân viên' : 'Không phải là nhân viên'}
            </Tag>
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default Profile;