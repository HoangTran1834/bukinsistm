import React from "react";
import { Layout, Menu, Button, Drawer } from "antd";
import { Link, useLocation } from "react-router-dom";
import { MenuOutlined } from "@ant-design/icons";
import { useAuth } from "@/contexts/AuthContext";
import UserDropdown from "@/components/UserDropdown";
import { isAdmin, isStaff, isDriver } from "@/constants/roles";

const { Header } = Layout;

const Navbar: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();
  const [visible, setVisible] = React.useState(false);

  const toggleDrawer = () => {
    setVisible(!visible);
  };

  // Define menu items based on authentication status and user role
  const items = [
    {
      key: "/",
      label: <Link to="/">Trang chủ</Link>,
    },
  ];

  // Only show these items if user is authenticated
  if (isAuthenticated && user) {
    // Add booking-related items for all authenticated users
    items.push({
      key: "/booking",
      label: <Link to="/booking">Đặt xe</Link>,
    });

    // Admin and staff can manage shifts
    if (isAdmin(user.vaitro) || isStaff(user.vaitro)) {
      items.push({
        key: "/shifts",
        label: <Link to="/shifts">Quản lý ca</Link>,
      });

      items.push({
        key: "/users",
        label: <Link to="/users">Quản lý người dùng</Link>,
      });
    }

    // Drivers can see their assigned shifts
    if (isDriver(user.vaitro)) {
      items.push({
        key: "/driver-shifts",
        label: <Link to="/driver-shifts">Ca làm việc</Link>,
      });
    }

    // All users can access their profile
    items.push({
      key: "/profile",
      label: <Link to="/profile">Hồ sơ</Link>,
    });
  }

  return (
    <Header
      style={{
        background: "#fff",
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        padding: "0 20px",
        position: "sticky",
        top: 0,
        zIndex: 1,
        width: "100%",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center" }}>
          <Link to="/" style={{ display: "flex", alignItems: "center" }}>
            <h1 style={{ margin: 0, fontSize: "20px", marginRight: "20px" }}>
              Hệ Thống Đặt Xe
            </h1>
          </Link>

          {/* Desktop Menu */}
          <div
            className="desktop-menu"
            style={{
              display: "none",
              "@media (min-width: 768px)": { display: "block" },
            }}
          >
            <Menu
              theme="light"
              mode="horizontal"
              selectedKeys={[location.pathname]}
              items={items}
              style={{ border: "none" }}
            />
          </div>

          {/* Mobile Menu Button */}
          <Button
            className="mobile-menu-button"
            type="text"
            icon={<MenuOutlined />}
            onClick={toggleDrawer}
            style={{
              display: "block",
              "@media (min-width: 768px)": { display: "none" },
            }}
          />
        </div>

        <div>
          {isAuthenticated ? (
            <UserDropdown />
          ) : (
            <div>
              <Link to="/login">
                <Button type="primary" style={{ marginRight: 10 }}>
                  Đăng nhập
                </Button>
              </Link>
              <Link to="/register">
                <Button>Đăng ký</Button>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      <Drawer
        title="Menu"
        placement="left"
        closable={true}
        onClose={toggleDrawer}
        open={visible}
      >
        <Menu
          mode="vertical"
          selectedKeys={[location.pathname]}
          items={items}
          style={{ border: "none" }}
        />
      </Drawer>
    </Header>
  );
};

export default Navbar;
