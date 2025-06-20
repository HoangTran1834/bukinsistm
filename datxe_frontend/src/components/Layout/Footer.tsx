import React from "react";
import {
  EnvironmentOutlined,
  MailOutlined,
  PhoneOutlined,
} from "@ant-design/icons";
import { Col, Divider, Layout, Row, Space, Typography } from "antd";

const { Footer: AntFooter } = Layout;
const { Title, Text, Link } = Typography;

const Footer: React.FC = () => {
  return (
    <AntFooter
      style={{
        backgroundColor: "#001529",
        color: "white",
        padding: "40px 20px 20px",
      }}
    >
      <Row gutter={[32, 32]}>
        <Col xs={24} sm={12} md={8}>
          <Title level={4} style={{ color: "white", marginBottom: 16 }}>
            Hệ thống đặt xe
          </Title>
          <Text style={{ color: "#ccc" }}>
            Dịch vụ đặt xe chất lượng cao, tin cậy và nhanh chóng.
          </Text>
        </Col>

        <Col xs={24} sm={12} md={8}>
          <Title level={5} style={{ color: "white", marginBottom: 16 }}>
            Liên hệ
          </Title>
          <Space direction="vertical" size="small">
            <Space>
              <PhoneOutlined style={{ color: "#1890ff" }} />
              <Link style={{ color: "#ccc" }}>0934913033</Link>
            </Space>
            <Space>
              <MailOutlined style={{ color: "#1890ff" }} />
              <Link style={{ color: "#ccc" }}>support@datxe.com</Link>
            </Space>
            <Space>
              <EnvironmentOutlined style={{ color: "#1890ff" }} />
              <Text style={{ color: "#ccc" }}>Đà Nẵng, Việt Nam</Text>
            </Space>
          </Space>
        </Col>

        <Col xs={24} sm={12} md={8}>
          <Title level={5} style={{ color: "white", marginBottom: 16 }}>
            Theo dõi chúng tôi
          </Title>
          <Space direction="vertical" size="small">
            <Link href="#" target="_blank" style={{ color: "#ccc" }}>
              Facebook
            </Link>
            <Link href="#" target="_blank" style={{ color: "#ccc" }}>
              Twitter
            </Link>
            <Link href="#" target="_blank" style={{ color: "#ccc" }}>
              Instagram
            </Link>
          </Space>
        </Col>
      </Row>

      <Divider style={{ borderColor: "#434343", margin: "32px 0 16px" }} />

      <Row justify="space-between" align="middle" style={{ marginTop: 24 }}>
        <Col>
          <Text type="secondary" style={{ color: "#8c8c8c" }}>
            © {new Date().getFullYear()} Hệ Thống Đặt Xe. All Rights Reserved.
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
