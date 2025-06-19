import React from "react";
import { Result, Button } from "antd";
import { Link } from "react-router-dom";

const NotFound: React.FC = () => {
  return (
    <Result
      status="404"
      title="404"
      subTitle="Trang bạn tìm kiếm không tồn tại."
      extra={
        <Link to="/">
          <Button type="primary">Về trang chủ</Button>
        </Link>
      }
    />
  );
};

export default NotFound;
        title={
          <Title level={1} style={{ fontSize: "4rem", marginBottom: "0" }}>
            404
          </Title>
        }
        subTitle={
          <Space direction="vertical" size="small" align="center">
            <Title level={3} style={{ marginTop: "0" }}>
              Oops! Trang không tìm thấy
            </Title>
            <Text type="secondary">
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

export default NotFoundPage;
