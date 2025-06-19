import { Button, Form, Input, notification } from "antd";
import { registerUserAPI } from "../services/api.service";

const RegisterPage = () => {
  const [form] = Form.useForm();

  const onFinish = async (values: any) => {
    console.log("Success:", values);

    const res = await registerUserAPI(
      values.hoten,
      values.sodienthoai,
      values.password,
      values.email
    );

    if (res.data) {
      notification.success({
        message: "Đăng ký",
        description: "Đăng ký thành công!",
      });
    } else {
      notification.error({
        message: "Đăng ký",
        description: Array.isArray(res?.message)
          ? res?.message.join(", ")
          : res?.message,
      });
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={onFinish}
      // onFinishFailed={onFinishFailed}
    >
      <div
        style={{
          margin: "50px",
        }}
      >
        <Form.Item
          label="Họ tên"
          name="hoten"
          rules={[{ required: true, message: "Vui lòng nhập họ tên!" }]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          label="Số điện thoại"
          name="sodienthoai"
          rules={[
            {
              required: true,
              pattern: new RegExp(/\d+/g),
              message: "Số điện thoại không hợp lệ!",
            },
          ]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          label="Mật khẩu"
          name="password"
          rules={[{ required: true, message: "Vui lòng nhập mật khẩu!" }]}
        >
          <Input.Password />
        </Form.Item>

        <Form.Item
          label="Email"
          name="email"
          rules={[
            { type: "email", message: "Email không hợp lệ!" },
            { required: false, message: "Vui lòng nhập email!" },
          ]}
        >
          <Input />
        </Form.Item>

        <Button type="primary">Register</Button>
      </div>
    </Form>
  );
};

export default RegisterPage;
