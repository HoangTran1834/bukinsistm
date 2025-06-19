import React from "react";
import { Dropdown, Avatar, Space } from "antd";
import {
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import type { MenuProps } from "antd";

const UserDropdown: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const items: MenuProps["items"] = [
    {
      key: "profile",
      label: "Hồ sơ cá nhân",
      icon: <UserOutlined />,
      onClick: () => navigate("/profile"),
    },
    {
      key: "settings",
      label: "Cài đặt tài khoản",
      icon: <SettingOutlined />,
      onClick: () => navigate("/settings"),
    },
    {
      type: "divider",
    },
    {
      key: "logout",
      label: "Đăng xuất",
      icon: <LogoutOutlined />,
      onClick: handleLogout,
    },
  ];

  return (
    <Dropdown menu={{ items }} trigger={["click"]}>
      <Space style={{ cursor: "pointer" }}>
        <Avatar icon={<UserOutlined />} />
        <span>{user?.hoTen || "Người dùng"}</span>
      </Space>
    </Dropdown>
  );
};

export default UserDropdown;
