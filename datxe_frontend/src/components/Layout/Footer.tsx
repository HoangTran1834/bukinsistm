import {
  EnvironmentOutlined,
  MailOutlined,
  PhoneOutlined,
} from "@ant-design/icons";
import { Col, Divider, Layout, Row, Space, Typography } from "antd";

const { Footer: AntFooter } = Layout;
const { Title, Text, Link } = Typography;

const Footer = () => {
  return (
    <AntFooter
      style={{
        backgroundColor: "#001529",
        color: "white",
        padding: "40px 20px 20px",
      }}
    >
      <Row gutter={[32, 32]}>
        <Col xs={24} sm={12} md={6}>
          <Title level={4} style={{ color: "white", marginBottom: 16 }}>
            DatXe System
          </Title>
          <Text style={{ color: "#ccc" }}>
            Hệ thống đặt xe trực tuyến hàng đầu Việt Nam. Kết nối hành khách và
            tài xế một cách nhanh chóng, an toàn.
          </Text>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Title level={5} style={{ color: "white", marginBottom: 16 }}>
            Dịch vụ
          </Title>
          <Space direction="vertical" size="small">
            <Link style={{ color: "#ccc" }}>Đặt xe ngay</Link>
            <Link style={{ color: "#ccc" }}>Đặt xe theo lịch</Link>
            <Link style={{ color: "#ccc" }}>Thuê xe dài hạn</Link>
            <Link style={{ color: "#ccc" }}>Dịch vụ giao hàng</Link>
          </Space>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Title level={5} style={{ color: "white", marginBottom: 16 }}>
            Hỗ trợ
          </Title>
          <Space direction="vertical" size="small">
            <Link style={{ color: "#ccc" }}>Trung tâm trợ giúp</Link>
            <Link style={{ color: "#ccc" }}>Điều khoản sử dụng</Link>
            <Link style={{ color: "#ccc" }}>Chính sách bảo mật</Link>
            <Link style={{ color: "#ccc" }}>Câu hỏi thường gặp</Link>
          </Space>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Title level={5} style={{ color: "white", marginBottom: 16 }}>
            Liên hệ
          </Title>
          <Space direction="vertical" size="small">
            <Space>
              <PhoneOutlined style={{ color: "#1890ff" }} />
              <Link style={{ color: "#ccc" }}>1900 1234</Link>
            </Space>
            <Space>
              <MailOutlined style={{ color: "#1890ff" }} />
              <Link style={{ color: "#ccc" }}>support@datxe.com</Link>
            </Space>
            <Space>
              <EnvironmentOutlined style={{ color: "#1890ff" }} />
              <Text style={{ color: "#ccc" }}>Hà Nội, Việt Nam</Text>
            </Space>
          </Space>
        </Col>
      </Row>

      <Divider style={{ borderColor: "#434343", margin: "32px 0 16px" }} />

      <Row justify="space-between" align="middle">
        <Col>
          <Text style={{ color: "#8c8c8c" }}>
            © 2024 DatXe System. All rights reserved.
          </Text>
        </Col>
        <Col>
          <Space>
            <Link style={{ color: "#8c8c8c" }}>Privacy</Link>
            <Link style={{ color: "#8c8c8c" }}>Terms</Link>
            <Link style={{ color: "#8c8c8c" }}>Contact</Link>
          </Space>
        </Col>
      </Row>
    </AntFooter>
  );
};

export default Footer;
