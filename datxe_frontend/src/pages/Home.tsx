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
import { useAuth } from "../contexts/authContext";

const { Title, Text, Paragraph } = Typography;

const Home: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  // Hero section background image
  // Bạn có thể thêm ảnh hero vào: /public/images/hero-banner.jpg
  // Hoặc import: import heroBg from '@/assets/images/banners/hero.jpg';

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
      </div>      {/* Routes Section */}
      <div style={{ background: "#f0f2f5", padding: "60px 0" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 16px" }}>
          <Title level={2} style={{ textAlign: "center", marginBottom: 16 }}>
            Các tuyến phổ biến
          </Title>
          <Paragraph style={{ textAlign: "center", marginBottom: 48, fontSize: 16, color: "#666" }}>
            Những tuyến đường được khách hàng lựa chọn nhiều nhất
          </Paragraph>

          <Row gutter={[24, 24]}>
            <Col xs={24} md={8}>
              <Card 
                style={{ 
                  height: "100%", 
                  borderRadius: 12,
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  transition: "all 0.3s"
                }}
                className="route-card"
                hoverable
              >
                <div style={{ textAlign: "center", marginBottom: 16 }}>
                  <div style={{
                    width: 60,
                    height: 60,
                    borderRadius: "50%",
                    background: "linear-gradient(135deg, #1890ff, #096dd9)",
                    margin: "0 auto 16px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                  }}>
                    <CarOutlined style={{ fontSize: 24, color: "white" }} />
                  </div>
                  <Title level={4} style={{ margin: 0, color: "#1890ff" }}>
                    Đà Nẵng ⇄ Tam Kỳ
                  </Title>
                </div>
                
                <div style={{ marginBottom: 16 }}>
                  <Row justify="space-between" style={{ marginBottom: 8 }}>
                    <Text strong>Giá vé:</Text>
                    <Text style={{ color: "#52c41a", fontWeight: "bold", fontSize: 16 }}>
                      100.000đ/người
                    </Text>
                  </Row>
                  <Row justify="space-between" style={{ marginBottom: 8 }}>
                    <Text strong>Thời gian:</Text>
                    <Text>~1.5 giờ</Text>
                  </Row>
                  <Row justify="space-between" style={{ marginBottom: 8 }}>
                    <Text strong>Khoảng cách:</Text>
                    <Text>~85 km</Text>
                  </Row>
                  <Row justify="space-between">
                    <Text strong>Số ca/ngày:</Text>
                    <Text>8 - 12 ca</Text>
                  </Row>
                </div>
                
                <Button 
                  type="primary" 
                  onClick={goToBooking}
                  style={{ width: "100%", borderRadius: 8 }}
                  size="large"
                >
                  Đặt vé ngay
                </Button>
              </Card>
            </Col>

            <Col xs={24} md={8}>
              <Card 
                style={{ 
                  height: "100%", 
                  borderRadius: 12,
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  transition: "all 0.3s"
                }}
                className="route-card"
                hoverable
              >
                <div style={{ textAlign: "center", marginBottom: 16 }}>
                  <div style={{
                    width: 60,
                    height: 60,
                    borderRadius: "50%",
                    background: "linear-gradient(135deg, #52c41a, #389e0d)",
                    margin: "0 auto 16px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                  }}>
                    <CarOutlined style={{ fontSize: 24, color: "white" }} />
                  </div>
                  <Title level={4} style={{ margin: 0, color: "#52c41a" }}>
                    Đà Nẵng ⇄ Thăng Bình
                  </Title>
                </div>
                
                <div style={{ marginBottom: 16 }}>
                  <Row justify="space-between" style={{ marginBottom: 8 }}>
                    <Text strong>Giá vé:</Text>
                    <Text style={{ color: "#52c41a", fontWeight: "bold", fontSize: 16 }}>
                      80.000đ/người
                    </Text>
                  </Row>
                  <Row justify="space-between" style={{ marginBottom: 8 }}>
                    <Text strong>Thời gian:</Text>
                    <Text>~1 giờ</Text>
                  </Row>
                  <Row justify="space-between" style={{ marginBottom: 8 }}>
                    <Text strong>Khoảng cách:</Text>
                    <Text>~65 km</Text>
                  </Row>
                  <Row justify="space-between">
                    <Text strong>Số ca/ngày:</Text>
                    <Text>6 - 10 ca</Text>
                  </Row>
                </div>
                
                <Button 
                  type="primary" 
                  onClick={goToBooking}
                  style={{ width: "100%", borderRadius: 8, background: "#52c41a", borderColor: "#52c41a" }}
                  size="large"
                >
                  Đặt vé ngay
                </Button>
              </Card>
            </Col>

            <Col xs={24} md={8}>
              <Card 
                style={{ 
                  height: "100%", 
                  borderRadius: 12,
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  transition: "all 0.3s"
                }}
                className="route-card"
                hoverable
              >
                <div style={{ textAlign: "center", marginBottom: 16 }}>
                  <div style={{
                    width: 60,
                    height: 60,
                    borderRadius: "50%",
                    background: "linear-gradient(135deg, #fa8c16, #d4380d)",
                    margin: "0 auto 16px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                  }}>
                    <CarOutlined style={{ fontSize: 24, color: "white" }} />
                  </div>
                  <Title level={4} style={{ margin: 0, color: "#fa8c16" }}>
                    Đà Nẵng ⇄ Quế Sơn
                  </Title>
                </div>
                
                <div style={{ marginBottom: 16 }}>
                  <Row justify="space-between" style={{ marginBottom: 8 }}>
                    <Text strong>Giá vé:</Text>
                    <Text style={{ color: "#52c41a", fontWeight: "bold", fontSize: 16 }}>
                      70.000đ/người
                    </Text>
                  </Row>
                  <Row justify="space-between" style={{ marginBottom: 8 }}>
                    <Text strong>Thời gian:</Text>
                    <Text>~1.2 giờ</Text>
                  </Row>
                  <Row justify="space-between" style={{ marginBottom: 8 }}>
                    <Text strong>Khoảng cách:</Text>
                    <Text>~75 km</Text>
                  </Row>
                  <Row justify="space-between">
                    <Text strong>Số ca/ngày:</Text>
                    <Text>5 - 8 ca</Text>
                  </Row>
                </div>
                
                <Button 
                  type="primary" 
                  onClick={goToBooking}
                  style={{ width: "100%", borderRadius: 8, background: "#fa8c16", borderColor: "#fa8c16" }}
                  size="large"
                >
                  Đặt vé ngay
                </Button>
              </Card>
            </Col>
          </Row>
            <div style={{ textAlign: "center", marginTop: 32 }}>
            <div style={{ 
              background: "rgba(255, 255, 255, 0.9)",
              borderRadius: 12,
              padding: 20,
              border: "1px solid #e8f4f8",
              marginBottom: 16
            }}>
              <Text style={{ fontSize: 15, color: "#1890ff", fontWeight: "500" }}>
                💡 <strong>Mẹo đặt vé:</strong> Đặt vé trước 2-3 giờ để có giá tốt nhất và đảm bảo có chỗ ngồi
              </Text>
            </div>
            <div style={{ 
              background: "rgba(255, 255, 255, 0.9)",
              borderRadius: 12,
              padding: 20,
              border: "1px solid #e8f4f8"
            }}>
              <Text style={{ fontSize: 15, color: "#52c41a", fontWeight: "500" }}>
                🎁 <strong>Ưu đãi:</strong> Giảm 10% cho khách hàng đặt vé lần đầu. Giảm 5% khi đặt vé khứ hồi
              </Text>
            </div>
          </div>
        </div>
      </div>

      {/* User Welcome Section */}
      {isAuthenticated && user && (
        <div style={{ maxWidth: 1200, margin: "60px auto", padding: "0 16px" }}>
          <Alert
            message={`Xin chào, ${user.hoten}!`}
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
      )}      {/* Stats Section */}
      <div style={{ 
        background: "linear-gradient(135deg, #f6f9fc 0%, #e9f4ff 100%)", 
        padding: "60px 0" 
      }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 16px" }}>
          <Title level={2} style={{ textAlign: "center", marginBottom: 16 }}>
            Con số ấn tượng
          </Title>
          <Paragraph style={{ textAlign: "center", marginBottom: 48, fontSize: 16, color: "#666" }}>
            Những thành tựu mà chúng tôi tự hào đạt được
          </Paragraph>

          <Row gutter={[32, 32]} justify="center">
            <Col xs={24} sm={12} md={6}>
              <Card 
                style={{ 
                  textAlign: "center", 
                  borderRadius: 16,
                  background: "linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)",
                  border: "1px solid #e3f2fd",
                  height: "100%"
                }} 
                bordered={false}
                className="stats-card"
              >
                <div style={{
                  width: 60,
                  height: 60,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #1890ff, #096dd9)",
                  margin: "0 auto 16px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}>
                  <TeamOutlined style={{ fontSize: 24, color: "white" }} />
                </div>
                <Statistic 
                  title={<span style={{ color: "#666", fontSize: 14 }}>Khách hàng</span>}
                  value={5000} 
                  suffix="+" 
                  valueStyle={{ color: "#1890ff", fontSize: 28, fontWeight: "bold" }}
                />
                <Text style={{ color: "#999", fontSize: 12 }}>Tin tưởng lựa chọn</Text>
              </Card>
            </Col>

            <Col xs={24} sm={12} md={6}>
              <Card 
                style={{ 
                  textAlign: "center", 
                  borderRadius: 16,
                  background: "linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)",
                  border: "1px solid #f6ffed",
                  height: "100%"
                }} 
                bordered={false}
                className="stats-card"
              >
                <div style={{
                  width: 60,
                  height: 60,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #52c41a, #389e0d)",
                  margin: "0 auto 16px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}>
                  <CarOutlined style={{ fontSize: 24, color: "white" }} />
                </div>
                <Statistic 
                  title={<span style={{ color: "#666", fontSize: 14 }}>Chuyến xe</span>}
                  value={15000} 
                  suffix="+" 
                  valueStyle={{ color: "#52c41a", fontSize: 28, fontWeight: "bold" }}
                />
                <Text style={{ color: "#999", fontSize: 12 }}>Hoàn thành thành công</Text>
              </Card>
            </Col>

            <Col xs={24} sm={12} md={6}>
              <Card 
                style={{ 
                  textAlign: "center", 
                  borderRadius: 16,
                  background: "linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)",
                  border: "1px solid #fff7e6",
                  height: "100%"
                }} 
                bordered={false}
                className="stats-card"
              >
                <div style={{
                  width: 60,
                  height: 60,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #fa8c16, #d4380d)",
                  margin: "0 auto 16px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}>
                  <SafetyOutlined style={{ fontSize: 24, color: "white" }} />
                </div>
                <Statistic 
                  title={<span style={{ color: "#666", fontSize: 14 }}>Tài xế</span>}
                  value={50} 
                  suffix="+" 
                  valueStyle={{ color: "#fa8c16", fontSize: 28, fontWeight: "bold" }}
                />
                <Text style={{ color: "#999", fontSize: 12 }}>Chuyên nghiệp, kinh nghiệm</Text>
              </Card>
            </Col>

            <Col xs={24} sm={12} md={6}>
              <Card 
                style={{ 
                  textAlign: "center", 
                  borderRadius: 16,
                  background: "linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)",
                  border: "1px solid #f9f0ff",
                  height: "100%"
                }} 
                bordered={false}
                className="stats-card"
              >
                <div style={{
                  width: 60,
                  height: 60,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #722ed1, #531dab)",
                  margin: "0 auto 16px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}>
                  <FieldTimeOutlined style={{ fontSize: 24, color: "white" }} />
                </div>
                <Statistic 
                  title={<span style={{ color: "#666", fontSize: 14 }}>Tuyến đường</span>}
                  value={20} 
                  suffix="+" 
                  valueStyle={{ color: "#722ed1", fontSize: 28, fontWeight: "bold" }}
                />
                <Text style={{ color: "#999", fontSize: 12 }}>Kết nối khắp khu vực</Text>
              </Card>
            </Col>
          </Row>
          
          <div style={{ 
            textAlign: "center", 
            marginTop: 40,
            padding: 24,
            background: "rgba(255, 255, 255, 0.7)",
            borderRadius: 12,
            border: "1px solid #e8f4f8"
          }}>
            <Text style={{ 
              fontSize: 16, 
              color: "#1890ff",
              fontWeight: "500"
            }}>
              🎯 <strong>Cam kết:</strong> Luôn mang đến dịch vụ tốt nhất với giá cả hợp lý và chất lượng vượt trội
            </Text>
          </div>
        </div>
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
