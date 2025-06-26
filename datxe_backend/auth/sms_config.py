# SMS OTP Configuration
SMS_CONFIG = {
    # OTP Settings
    'OTP_LENGTH': 6,                    # Độ dài OTP (6 số)
    'OTP_EXPIRE_MINUTES': 5,            # OTP hết hạn sau 5 phút
    'OTP_MAX_ATTEMPTS': 5,              # Tối đa 3 lần nhập sai
    'OTP_RESEND_COOLDOWN_SECONDS': 30,  # Phải đợi 60s mới được gửi lại OTP
    
    # Rate Limiting
    'MAX_OTP_REQUESTS_PER_PHONE_PER_HOUR': 5,  # Tối đa 5 OTP/số điện thoại/giờ
    'BLOCK_PHONE_AFTER_FAILED_ATTEMPTS': 10,   # Block số điện thoại sau 10 lần thất bại
    'PHONE_BLOCK_DURATION_HOURS': 24,          # Block trong 24 giờ
    
    # Cache Keys Prefix
    'CACHE_PREFIX': 'sms_otp',
    'SIGNUP_OTP_PREFIX': 'signup_otp',
    'LOGIN_OTP_PREFIX': 'login_otp',
    'ATTEMPTS_PREFIX': 'otp_attempts',
    'PHONE_BLOCK_PREFIX': 'phone_blocked',
    'RESEND_COOLDOWN_PREFIX': 'resend_cooldown',
      # SMS Templates (Mô phỏng)
    'SMS_TEMPLATES': {
        'SIGNUP': 'Mã xác thực đăng ký tài khoản: {otp}. Có hiệu lực trong {expire_minutes} phút.',
        'LOGIN': 'Mã xác thực đăng nhập: {otp}. Có hiệu lực trong {expire_minutes} phút.',
        'RESET_PASSWORD': 'Mã xác thực đặt lại mật khẩu: {otp}. Có hiệu lực trong {expire_minutes} phút.',
    },
    
    # Development Settings
    'SIMULATE_SMS': True,  # True = mô phỏng SMS, False = gửi SMS thật
    'DEVELOPMENT_OTP': None,  # None = OTP ngẫu nhiên, "123456" = OTP cố định cho dev
}

# Error Messages
SMS_ERROR_MESSAGES = {
    'OTP_EXPIRED': 'Mã OTP đã hết hạn. Vui lòng yêu cầu mã mới.',
    'OTP_INVALID': 'Mã OTP không đúng.',
    'OTP_MAX_ATTEMPTS': 'Bạn đã nhập sai quá {max_attempts} lần. Vui lòng yêu cầu mã OTP mới.',
    'PHONE_BLOCKED': 'Số điện thoại này đã bị tạm khóa do quá nhiều lần thất bại. Vui lòng thử lại sau {hours} giờ.',
    'RESEND_COOLDOWN': 'Vui lòng đợi {seconds} giây trước khi yêu cầu mã OTP mới.',
    'MAX_REQUESTS_EXCEEDED': 'Bạn đã vượt quá giới hạn yêu cầu OTP. Vui lòng thử lại sau 1 giờ.',
    'PHONE_NOT_FOUND': 'Không tìm thấy tài khoản với số điện thoại này.',
    'PHONE_ALREADY_EXISTS': 'Số điện thoại này đã được đăng ký.',
}
