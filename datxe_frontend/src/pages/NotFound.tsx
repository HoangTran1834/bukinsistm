import React from "react";
import { Result, Button, Typography, Space } from "antd";
import { Link } from "react-router-dom";
import { HomeOutlined } from "@ant-design/icons";

const { Title, Text } = Typography;

const NotFound: React.FC = () => {
  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    }}>
      <Result
        status="404"
        title={
          <Title level={1} style={{ fontSize: "4rem", marginBottom: "0", color: "#fff" }}>
            404
          </Title>
        }
        subTitle={
          <Space direction="vertical" size="small" align="center">
            <Title level={3} style={{ marginTop: "0", color: "#fff" }}>
              Oops! Trang không tìm thấy
            </Title>
            <Text style={{ color: "#f0f0f0" }}>
              Trang bạn đang tìm kiếm không tồn tại hoặc đã bị di chuyển.
            </Text>
          </Space>
        }
        extra={
          <Link to="/">
            <Button
              type="primary"
              size="large"
              icon={<HomeOutlined />}
              style={{
                borderRadius: "50px",
                height: "50px",
                paddingLeft: "30px",
                paddingRight: "30px",
                fontSize: "16px",
                boxShadow: "0 8px 16px rgba(24, 144, 255, 0.2)",
              }}
            >
              Về Trang Chủ
            </Button>
          </Link>
        }
      />
    </div>
  );
};

export default NotFound;
