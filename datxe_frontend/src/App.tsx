import React from "react";
import { Outlet } from "react-router-dom";
import { Layout, ConfigProvider } from "antd";
import viVN from "antd/lib/locale/vi_VN";
import { AuthProvider } from "./contexts/authContext";
import Navbar from "./components/Layout/Navbar";
import Footer from "./components/Layout/Footer";
import "./App.css";

const { Content } = Layout;

// Root App component with layout
const App: React.FC = () => {
  return (
    <ConfigProvider locale={viVN}>
      <AuthProvider>
        <Layout style={{ minHeight: "100vh" }}>
          <Navbar />
          <Content style={{ padding: "0 0 24px 0", flex: 1 }}>            
            <Outlet />
          </Content>
          <Footer />
        </Layout>
      </AuthProvider>
    </ConfigProvider>
  );
};

export default App;
