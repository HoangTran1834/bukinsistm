import {
  CarOutlined,
  ClockCircleOutlined,
  DollarOutlined,
  RightCircleFilled,
  SafetyOutlined,
  StarFilled,
} from "@ant-design/icons";
import {
  Button,
  Card,
  Carousel,
  Col,
  Layout,
  Row,
  Space,
  Statistic,
  Typography,
} from "antd";

const { Title, Paragraph } = Typography;
const { Content } = Layout;

const HomePage = () => {
  return (
    <Content className="home-page">
      {/* Hero Banner */}
      <div
        className="hero-section"
        style={{
          backgroundImage:
            "linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), url(/images/taxi-banner.jpg)",
          backgroundSize: "cover",
          backgroundPosition: "center",
          color: "white",
          padding: "80px 20px",
          textAlign: "center",
          marginBottom: "40px",
        }}
      >
        <Title style={{ color: "white", fontSize: "2.5rem" }}>
          ĐẶT XE NHANH CHÓNG & TIỆN LỢI
        </Title>
        <Paragraph
          style={{
            color: "white",
            fontSize: "1.2rem",
            maxWidth: "800px",
            margin: "20px auto",
          }}
        >
          Giải pháp đặt xe hiện đại, an toàn và tiết kiệm chi phí. Đồng hành
          cùng bạn trên mọi hành trình.
        </Paragraph>
        <Space size="large">
          <Button type="primary" size="large" icon={<CarOutlined />}>
            Đặt xe ngay
          </Button>
          <Button size="large" ghost>
            Tìm hiểu thêm
          </Button>
        </Space>
      </div>

      {/* Features Section */}
      <div
        className="features-section"
        style={{ padding: "40px 20px", background: "#f7f7f7" }}
      >
        <Title level={2} style={{ textAlign: "center", marginBottom: "40px" }}>
          Tại sao chọn chúng tôi?
        </Title>
        <Row gutter={[24, 24]} justify="center">
          <Col xs={24} sm={12} md={8}>
            <Card className="feature-card" hoverable>
              <SafetyOutlined
                style={{
                  fontSize: "48px",
                  color: "#1890ff",
                  marginBottom: "20px",
                }}
              />
              <Title level={4}>An toàn là ưu tiên hàng đầu</Title>
              <Paragraph>
                Tất cả tài xế đều được đào tạo chuyên nghiệp và kiểm tra lý
                lịch. Xe được bảo dưỡng định kỳ.
              </Paragraph>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card className="feature-card" hoverable>
              <ClockCircleOutlined
                style={{
                  fontSize: "48px",
                  color: "#1890ff",
                  marginBottom: "20px",
                }}
              />
              <Title level={4}>Đặt xe nhanh chóng</Title>
              <Paragraph>
                Chỉ với vài thao tác đơn giản, xe sẽ đến đón bạn trong thời gian
                sớm nhất.
              </Paragraph>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card className="feature-card" hoverable>
              <DollarOutlined
                style={{
                  fontSize: "48px",
                  color: "#1890ff",
                  marginBottom: "20px",
                }}
              />
              <Title level={4}>Giá cả hợp lý</Title>
              <Paragraph>
                Mức giá cạnh tranh với nhiều ưu đãi và khuyến mãi hấp dẫn cho
                khách hàng thân thiết.
              </Paragraph>
            </Card>
          </Col>
        </Row>
      </div>

      {/* How It Works */}
      <div className="how-it-works" style={{ padding: "60px 20px" }}>
        <Title level={2} style={{ textAlign: "center", marginBottom: "40px" }}>
          Đặt xe chỉ với 3 bước đơn giản
        </Title>
        <Row gutter={[32, 32]} justify="center" align="middle">
          <Col xs={24} md={8}>
            <div className="step-card" style={{ textAlign: "center" }}>
              <div
                className="step-number"
                style={{
                  background: "#1890ff",
                  color: "white",
                  width: "60px",
                  height: "60px",
                  lineHeight: "60px",
                  fontSize: "24px",
                  borderRadius: "50%",
                  margin: "0 auto 20px",
                }}
              >
                1
              </div>
              <Title level={4}>Chọn điểm đón và điểm đến</Title>
              <Paragraph>
                Nhập địa điểm đón và điểm đến của bạn trên ứng dụng hoặc website
              </Paragraph>
            </div>
          </Col>
          <Col xs={24} md={8}>
            <div className="step-card" style={{ textAlign: "center" }}>
              <div
                className="step-number"
                style={{
                  background: "#1890ff",
                  color: "white",
                  width: "60px",
                  height: "60px",
                  lineHeight: "60px",
                  fontSize: "24px",
                  borderRadius: "50%",
                  margin: "0 auto 20px",
                }}
              >
                2
              </div>
              <Title level={4}>Chọn loại xe phù hợp</Title>
              <Paragraph>
                Lựa chọn phương tiện phù hợp với nhu cầu và ngân sách của bạn
              </Paragraph>
            </div>
          </Col>
          <Col xs={24} md={8}>
            <div className="step-card" style={{ textAlign: "center" }}>
              <div
                className="step-number"
                style={{
                  background: "#1890ff",
                  color: "white",
                  width: "60px",
                  height: "60px",
                  lineHeight: "60px",
                  fontSize: "24px",
                  borderRadius: "50%",
                  margin: "0 auto 20px",
                }}
              >
                3
              </div>
              <Title level={4}>Xác nhận và thanh toán</Title>
              <Paragraph>
                Xác nhận thông tin đặt xe và chọn phương thức thanh toán phù hợp
              </Paragraph>
            </div>
          </Col>
        </Row>
        <div style={{ textAlign: "center", marginTop: "40px" }}>
          <Button type="primary" size="large">
            Trải nghiệm ngay
          </Button>
        </div>
      </div>

      {/* Services */}
      <div
        className="services-section"
        style={{ padding: "60px 20px", background: "#f0f8ff" }}
      >
        <Title level={2} style={{ textAlign: "center", marginBottom: "40px" }}>
          Dịch vụ của chúng tôi
        </Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} sm={12} lg={6}>
            <Card
              hoverable
              cover={
                <div
                  style={{
                    height: "160px",
                    background: "#1890ff",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <CarOutlined style={{ fontSize: "64px", color: "white" }} />
                </div>
              }
            >
              <Card.Meta
                title="Xe 4 chỗ tiêu chuẩn"
                description="Phù hợp cho cá nhân và nhóm nhỏ, giá cả phải chăng"
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card
              hoverable
              cover={
                <div
                  style={{
                    height: "160px",
                    background: "#52c41a",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <CarOutlined style={{ fontSize: "64px", color: "white" }} />
                </div>
              }
            >
              <Card.Meta
                title="Xe 7 chỗ gia đình"
                description="Không gian rộng rãi cho gia đình và nhóm bạn"
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card
              hoverable
              cover={
                <div
                  style={{
                    height: "160px",
                    background: "#722ed1",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <CarOutlined style={{ fontSize: "64px", color: "white" }} />
                </div>
              }
            >
              <Card.Meta
                title="Xe VIP cao cấp"
                description="Trải nghiệm đẳng cấp với dòng xe sang và dịch vụ vượt trội"
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card
              hoverable
              cover={
                <div
                  style={{
                    height: "160px",
                    background: "#fa8c16",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <CarOutlined style={{ fontSize: "64px", color: "white" }} />
                </div>
              }
            >
              <Card.Meta
                title="Xe du lịch dài ngày"
                description="Giải pháp di chuyển tối ưu cho các chuyến du lịch dài ngày"
              />
            </Card>
          </Col>
        </Row>
      </div>

      {/* Testimonials */}
      <div className="testimonials" style={{ padding: "60px 20px" }}>
        <Title level={2} style={{ textAlign: "center", marginBottom: "40px" }}>
          Khách hàng nói gì về chúng tôi
        </Title>
        <Carousel autoplay style={{ maxWidth: "900px", margin: "0 auto" }}>
          <div>
            <Card style={{ margin: "20px" }}>
              <div style={{ textAlign: "center", padding: "20px" }}>
                <div
                  style={{
                    fontSize: "24px",
                    color: "#faad14",
                    marginBottom: "20px",
                  }}
                >
                  <StarFilled />
                  <StarFilled />
                  <StarFilled />
                  <StarFilled />
                  <StarFilled />
                </div>
                <Paragraph style={{ fontSize: "16px", fontStyle: "italic" }}>
                  "Dịch vụ đặt xe rất tiện lợi và nhanh chóng. Tài xế thân thiện
                  và chuyên nghiệp. Tôi sẽ tiếp tục sử dụng dịch vụ trong tương
                  lai."
                </Paragraph>
                <Title level={5}>Nguyễn Văn A</Title>
                <Paragraph>Khách hàng thường xuyên</Paragraph>
              </div>
            </Card>
          </div>
          <div>
            <Card style={{ margin: "20px" }}>
              <div style={{ textAlign: "center", padding: "20px" }}>
                <div
                  style={{
                    fontSize: "24px",
                    color: "#faad14",
                    marginBottom: "20px",
                  }}
                >
                  <StarFilled />
                  <StarFilled />
                  <StarFilled />
                  <StarFilled />
                  <StarFilled />
                </div>
                <Paragraph style={{ fontSize: "16px", fontStyle: "italic" }}>
                  "Ứng dụng rất dễ sử dụng, đặt xe nhanh chóng và thanh toán
                  linh hoạt. Giá cả cũng rất cạnh tranh so với các dịch vụ khác
                  trên thị trường."
                </Paragraph>
                <Title level={5}>Trần Thị B</Title>
                <Paragraph>Doanh nhân</Paragraph>
              </div>
            </Card>
          </div>
        </Carousel>
      </div>

      {/* Statistics */}
      <div
        className="statistics"
        style={{ padding: "60px 20px", background: "#001529", color: "white" }}
      >
        <Row gutter={[32, 32]} justify="center">
          <Col xs={12} md={6}>
            <Statistic
              title={
                <span style={{ color: "white" }}>Khách hàng hài lòng</span>
              }
              value={98}
              suffix="%"
              valueStyle={{ color: "#1890ff", fontSize: "2rem" }}
            />
          </Col>
          <Col xs={12} md={6}>
            <Statistic
              title={
                <span style={{ color: "white" }}>Chuyến xe hoàn thành</span>
              }
              value={50000}
              valueStyle={{ color: "#1890ff", fontSize: "2rem" }}
            />
          </Col>
          <Col xs={12} md={6}>
            <Statistic
              title={<span style={{ color: "white" }}>Tài xế đối tác</span>}
              value={1200}
              valueStyle={{ color: "#1890ff", fontSize: "2rem" }}
            />
          </Col>
          <Col xs={12} md={6}>
            <Statistic
              title={
                <span style={{ color: "white" }}>Thành phố hoạt động</span>
              }
              value={15}
              valueStyle={{ color: "#1890ff", fontSize: "2rem" }}
            />
          </Col>
        </Row>
      </div>

      {/* CTA Section */}
      <div
        className="cta-section"
        style={{ padding: "60px 20px", textAlign: "center" }}
      >
        <Title level={2}>
          Sẵn sàng trải nghiệm dịch vụ đặt xe của chúng tôi?
        </Title>
        <Paragraph
          style={{ fontSize: "16px", maxWidth: "700px", margin: "20px auto" }}
        >
          Đăng ký tài khoản ngay hôm nay để nhận nhiều ưu đãi hấp dẫn dành cho
          thành viên mới
        </Paragraph>
        <Space size="large">
          <Button type="primary" size="large" icon={<RightCircleFilled />}>
            Đăng ký ngay
          </Button>
          <Button size="large">Tìm hiểu thêm</Button>
        </Space>
      </div>
    </Content>
  );
};

export default HomePage;
