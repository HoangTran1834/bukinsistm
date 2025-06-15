import React from "react";

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-800 text-white mt-auto py-6">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-3">Hệ thống đặt xe</h3>
            <p className="text-sm text-gray-300">
              Dịch vụ đặt xe uy tín, tiện lợi cho người dùng, với đội ngũ tài xế
              chuyên nghiệp
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-3">Liên hệ</h3>
            <p className="text-sm text-gray-300">Email: contact@datxe.com</p>
            <p className="text-sm text-gray-300">Số điện thoại: 1900 1234</p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-3">Theo dõi chúng tôi</h3>
            <div className="flex space-x-3">
              <a href="#" className="text-gray-300 hover:text-white">
                Facebook
              </a>
              <a href="#" className="text-gray-300 hover:text-white">
                Instagram
              </a>
              <a href="#" className="text-gray-300 hover:text-white">
                Twitter
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-6 pt-6 text-center text-sm text-gray-400">
          © {currentYear} Hệ thống Đặt Xe. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
