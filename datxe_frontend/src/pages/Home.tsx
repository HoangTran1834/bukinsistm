import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Typography,
  Button,
  Row,
  Col,
  Card,
  Statistic,
  Space,
  Alert,
} from "antd";
import {
  CarOutlined,
  FieldTimeOutlined,
  SafetyOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import { useAuth } from "@/contexts/AuthContext";

const { Title, Text, Paragraph } = Typography;

const Home: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  const goToBooking = () => {
    if (isAuthenticated) {
      navigate("/booking");
    } else {
      navigate("/login", { state: { from: { pathname: "/booking" } } });
    }
  };

  return (
    <div className="home-container">
      {/* Hero Section */}
      <div
        className="hero-section"
        style={{
          background: "linear-gradient(135deg, #1890ff 0%, #096dd9 100%)",
          padding: "60px 0",
          color: "white",
          textAlign: "center",
        }}
      >
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 16px" }}>
          <Title level={1} style={{ color: "white", marginBottom: 24 }}>
            Hệ Thống Đặt Xe Nhanh Chóng & Tiện Lợi
          </Title>
          <Paragraph
            style={{
              fontSize: 18,
              marginBottom: 32,
              color: "rgba(255, 255, 255, 0.8)",
            }}
          >
            Dịch vụ đặt xe chất lượng cao, tin cậy và nhanh chóng cho chuyến đi
            của bạn
          </Paragraph>
          <Button
            type="primary"
            size="large"
            onClick={goToBooking}
            style={{
              height: 50,
              fontSize: 16,
              padding: "0 32px",
              background: "white",
              borderColor: "white",
              color: "#1890ff",
            }}
          >
            Đặt xe ngay
          </Button>
        </div>
      </div>

      {/* Features Section */}
      <div style={{ maxWidth: 1200, margin: "60px auto", padding: "0 16px" }}>
        <Title level={2} style={{ textAlign: "center", marginBottom: 48 }}>
          Tại sao chọn chúng tôi?
        </Title>

        <Row gutter={[32, 32]} justify="center">
          <Col xs={24} sm={12} md={6}>
            <Card
              style={{ height: "100%", textAlign: "center" }}
              bordered={false}
              className="feature-card"
            >
              <CarOutlined
                style={{
                  fontSize: 40,
                  color: "#1890ff",
                  marginBottom: 16,
                }}
              />
              <Title level={4}>Dịch vụ nhanh chóng</Title>
              <Text>Đặt xe trong vài phút, đón bạn đúng giờ</Text>
            </Card>
          </Col>

          <Col xs={24} sm={12} md={6}>
            <Card
              style={{ height: "100%", textAlign: "center" }}
              bordered={false}
              className="feature-card"
            >
              <SafetyOutlined
                style={{
                  fontSize: 40,
                  color: "#1890ff",
                  marginBottom: 16,
                }}
              />
              <Title level={4}>An toàn tin cậy</Title>
              <Text>Tài xế chuyên nghiệp, được đào tạo kỹ lưỡng</Text>
            </Card>
          </Col>

          <Col xs={24} sm={12} md={6}>
            <Card
              style={{ height: "100%", textAlign: "center" }}
              bordered={false}
              className="feature-card"
            >
              <FieldTimeOutlined
                style={{
                  fontSize: 40,
                  color: "#1890ff",
                  marginBottom: 16,
                }}
              />
              <Title level={4}>Đúng giờ</Title>
              <Text>Cam kết đón trả đúng thời gian đã hẹn</Text>
            </Card>
          </Col>

          <Col xs={24} sm={12} md={6}>
            <Card
              style={{ height: "100%", textAlign: "center" }}
              bordered={false}
              className="feature-card"
            >
              <TeamOutlined
                style={{
                  fontSize: 40,
                  color: "#1890ff",
                  marginBottom: 16,
                }}
              />
              <Title level={4}>Hỗ trợ 24/7</Title>
              <Text>Đội ngũ tư vấn luôn sẵn sàng phục vụ</Text>
            </Card>
          </Col>
        </Row>
      </div>

      {/* Routes Section */}
      <div style={{ background: "#f0f2f5", padding: "60px 0" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 16px" }}>
          <Title level={2} style={{ textAlign: "center", marginBottom: 48 }}>
            Các tuyến phổ biến
          </Title>

          <Row gutter={[32, 32]}>
            <Col xs={24} md={8}>
              <Card style={{ height: "100%" }}>
                <Title level={4}>Đà Nẵng → Tam Kỳ</Title>
                <Paragraph>
                  <Space>
                    <Text strong>Giá:</Text> <Text>100.000đ/người</Text>
                  </Space>
                </Paragraph>
                <Paragraph>
                  <Space>
                    <Text strong>Thời gian:</Text> <Text>~1.5 giờ</Text>
                  </Space>
                </Paragraph>
                <Button type="primary" onClick={goToBooking}>
                  Đặt ngay
                </Button>
              </Card>
            </Col>

            <Col xs={24} md={8}>
              <Card style={{ height: "100%" }}>
                <Title level={4}>Đà Nẵng → Thăng Bình</Title>
                <Paragraph>
                  <Space>
                    <Text strong>Giá:</Text> <Text>80.000đ/người</Text>
                  </Space>
                </Paragraph>
                <Paragraph>
                  <Space>
                    <Text strong>Thời gian:</Text> <Text>~1 giờ</Text>
                  </Space>
                </Paragraph>
                <Button type="primary" onClick={goToBooking}>
                  Đặt ngay
                </Button>
              </Card>
            </Col>

            <Col xs={24} md={8}>
              <Card style={{ height: "100%" }}>
                <Title level={4}>Đà Nẵng → Quế Sơn</Title>
                <Paragraph>
                  <Space>
                    <Text strong>Giá:</Text> <Text>70.000đ/người</Text>
                  </Space>
                </Paragraph>
                <Paragraph>
                  <Space>
                    <Text strong>Thời gian:</Text> <Text>~1.2 giờ</Text>
                  </Space>
                </Paragraph>
                <Button type="primary" onClick={goToBooking}>
                  Đặt ngay
                </Button>
              </Card>
            </Col>
          </Row>
        </div>
      </div>

      {/* User Welcome Section */}
      {isAuthenticated && user && (
        <div style={{ maxWidth: 1200, margin: "60px auto", padding: "0 16px" }}>
          <Alert
            message={`Xin chào, ${user.hoTen}!`}
            description={
              <div>
                <Paragraph>
                  Chúc bạn có một ngày tốt lành. Bạn đang đăng nhập với vai trò{" "}
                  {user.vaitro}.
                </Paragraph>
                <Button type="primary" onClick={goToBooking}>
                  Đặt xe ngay
                </Button>
              </div>
            }
            type="success"
            showIcon
          />
        </div>
      )}

      {/* Stats Section */}
      <div style={{ maxWidth: 1200, margin: "60px auto", padding: "0 16px" }}>
        <Title level={2} style={{ textAlign: "center", marginBottom: 48 }}>
          Con số ấn tượng
        </Title>

        <Row gutter={[32, 32]} justify="center">
          <Col xs={24} sm={12} md={6}>
            <Card style={{ textAlign: "center" }} bordered={false}>
              <Statistic title="Khách hàng" value={5000} suffix="+" />
            </Card>
          </Col>

          <Col xs={24} sm={12} md={6}>
            <Card style={{ textAlign: "center" }} bordered={false}>
              <Statistic title="Chuyến xe" value={15000} suffix="+" />
            </Card>
          </Col>

          <Col xs={24} sm={12} md={6}>
            <Card style={{ textAlign: "center" }} bordered={false}>
              <Statistic title="Tài xế" value={50} suffix="+" />
            </Card>
          </Col>

          <Col xs={24} sm={12} md={6}>
            <Card style={{ textAlign: "center" }} bordered={false}>
              <Statistic title="Tuyến đường" value={20} suffix="+" />
            </Card>
          </Col>
        </Row>
      </div>

      {/* CTA Section */}
      <div
        style={{
          background: "linear-gradient(135deg, #1890ff 0%, #096dd9 100%)",
          padding: "60px 0",
          color: "white",
          textAlign: "center",
          marginTop: 60,
        }}
      >
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 16px" }}>
          <Title level={2} style={{ color: "white", marginBottom: 24 }}>
            Sẵn sàng cho chuyến đi của bạn?
          </Title>
          <Paragraph
            style={{
              fontSize: 18,
              marginBottom: 32,
              color: "rgba(255, 255, 255, 0.8)",
            }}
          >
            Đặt xe ngay hôm nay để có trải nghiệm tốt nhất
          </Paragraph>
          <Button
            type="primary"
            size="large"
            onClick={goToBooking}
            style={{
              height: 50,
              fontSize: 16,
              padding: "0 32px",
              background: "white",
              borderColor: "white",
              color: "#1890ff",
            }}
          >
            Đặt xe ngay
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Home;
