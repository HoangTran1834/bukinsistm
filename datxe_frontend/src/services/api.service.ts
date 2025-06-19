import axios from "./axios.customize";

export const registerUserAPI = (
  hoten: string,
  sodienthoai: string,
  password: string,
  email: string
) => {
  const URL_BACKEND = "/signup";
  const data = {
    hoten: hoten,
    sodienthoai: sodienthoai,
    password: password,
    email: email,
  };

  return axios.post(URL_BACKEND, data);
};
