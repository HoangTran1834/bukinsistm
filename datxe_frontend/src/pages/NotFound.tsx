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
