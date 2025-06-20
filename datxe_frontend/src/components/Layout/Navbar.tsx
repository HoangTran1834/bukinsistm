import React from "react";
import { Layout, Menu, Button, Drawer } from "antd";
import { Link, useLocation } from "react-router-dom";
import { MenuOutlined } from "@ant-design/icons";
import { useAuth } from "../../contexts/authContext";
import { isAdmin, isStaff, isDriver } from "@/constants/roles";
import UserDropdown from "../UserDropdown";

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
    // Logo đã làm link về trang chủ, không cần menu item "Trang chủ" nữa
  ];

  // Only show these items if user is authenticated
  if (isAuthenticated && user) {
    // Add booking-related items for all authenticated users
    items.push({
      key: "/booking",
      label: <Link to="/booking">Đặt xe</Link>,
    });    // Admin and staff can manage shifts
    if (isAdmin(user.vaitro) || isStaff(user.vaitro)) {
      items.push({
        key: "/shifts",
        label: <Link to="/shifts">Quản lý ca</Link>,
      });
      
      // Staff can book for customers
      items.push({
        key: "/staff/booking",
        label: <Link to="/staff/booking">Đặt vé cho khách</Link>,
      });    }

    // Only Admin can access Django Admin Panel
    if (isAdmin(user.vaitro)) {
      // Django Admin Panel - chỉ cho Admin
      items.push({
        key: "/admin-panel",
        label: <a href={`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'}/admin/`} target="_blank" rel="noopener noreferrer">Django Admin</a>,
      });
    }

    // Drivers can see their assigned shifts
    if (isDriver(user.vaitro)) {
      items.push({
        key: "/driver-shifts",
        label: <Link to="/driver-shifts">Ca làm việc</Link>,
      });
    }

    // Profile đã có trong UserDropdown, không cần duplicate ở menu
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
          <Link to="/" style={{ display: "flex", alignItems: "center" }}>            {/* Logo - click để về trang chủ */}
            <div style={{
              backgroundColor: "white",
              borderRadius: "4px",
              padding: "4px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <img 
                src="/images/home.png"
                alt="Hệ Thống Đặt Xe" 
                style={{ 
                  height: "45px", 
                  objectFit: "contain",
                  cursor: "pointer",                  // Thử loại bỏ nền xám bằng filter mạnh hơn
                  filter: "brightness(1.5) contrast(1.3) saturate(1.2) hue-rotate(0deg)"
                }} 
              />
            </div>
          </Link>          {/* Desktop Menu - Hiển thị đầy đủ trên màn hình lớn */}
          <div 
            className="desktop-menu"
            style={{
              display: "flex",
              alignItems: "center", // Căn giữa theo chiều dọc
              marginLeft: "20px",
              gap: "20px",
              height: "64px" // Cùng chiều cao với Header
            }}
          >{items.map((item) => (
              <div key={item.key} style={{ 
                padding: "8px 12px",
                borderRadius: "4px",
                transition: "background-color 0.3s",
                cursor: "pointer",
                display: "flex",
                alignItems: "center", // Căn giữa nội dung trong item
                height: "45px" // Cùng chiều cao với logo
              }}>
                {item.label}
              </div>
            ))}
          </div>
        </div>        
        {/* Mobile Menu Button and Auth Buttons */}
        <div style={{ display: "flex", alignItems: "center" }}>
          <Button
            className="mobile-menu-button"
            type="text"            icon={<MenuOutlined />}
            onClick={toggleDrawer}
            style={{ 
              marginRight: 10, 
              display: "none" // Control bởi CSS responsive
            }}
          />
          {!isAuthenticated ? (
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
          ) : (
            <UserDropdown />
          )}
        </div>
      </div>      
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
        {isAuthenticated && (
          <div style={{ padding: "16px", borderTop: "1px solid #f0f0f0", marginTop: "16px" }}>
            <UserDropdown />
          </div>
        )}
      </Drawer>
    </Header>
  );
};

export default Navbar;
