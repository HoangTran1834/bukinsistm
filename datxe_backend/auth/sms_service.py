import random
import string
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone
from .sms_config import SMS_CONFIG, SMS_ERROR_MESSAGES

class SMSOTPService:
    """Service xử lý SMS OTP"""
    
    @staticmethod
    def generate_otp():
        """Tạo OTP ngẫu nhiên"""
        if SMS_CONFIG['DEVELOPMENT_OTP']:
            return SMS_CONFIG['DEVELOPMENT_OTP']
        
        length = SMS_CONFIG['OTP_LENGTH']
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def get_cache_key(prefix, phone_number):
        """Tạo cache key"""
        return f"{SMS_CONFIG['CACHE_PREFIX']}:{prefix}:{phone_number}"
    
    @staticmethod
    def is_phone_blocked(phone_number):
        """Kiểm tra số điện thoại có bị block không"""
        cache_key = SMSOTPService.get_cache_key(SMS_CONFIG['PHONE_BLOCK_PREFIX'], phone_number)
        return cache.get(cache_key, False)
    
    @staticmethod
    def block_phone(phone_number):
        """Block số điện thoại"""
        cache_key = SMSOTPService.get_cache_key(SMS_CONFIG['PHONE_BLOCK_PREFIX'], phone_number)
        timeout = SMS_CONFIG['PHONE_BLOCK_DURATION_HOURS'] * 3600  # Convert to seconds
        cache.set(cache_key, True, timeout)
    
    @staticmethod
    def is_resend_cooldown_active(phone_number):
        """Kiểm tra cooldown gửi lại OTP"""
        cache_key = SMSOTPService.get_cache_key(SMS_CONFIG['RESEND_COOLDOWN_PREFIX'], phone_number)
        return cache.get(cache_key, False)
    
    @staticmethod
    def set_resend_cooldown(phone_number):
        """Set cooldown gửi lại OTP"""
        cache_key = SMSOTPService.get_cache_key(SMS_CONFIG['RESEND_COOLDOWN_PREFIX'], phone_number)
        timeout = SMS_CONFIG['OTP_RESEND_COOLDOWN_SECONDS']
        cache.set(cache_key, True, timeout)
    
    @staticmethod
    def get_otp_attempts(phone_number, otp_type):
        """Lấy số lần thử OTP"""
        cache_key = SMSOTPService.get_cache_key(f"{SMS_CONFIG['ATTEMPTS_PREFIX']}_{otp_type}", phone_number)
        return cache.get(cache_key, 0)
    
    @staticmethod
    def increment_otp_attempts(phone_number, otp_type):
        """Tăng số lần thử OTP"""
        cache_key = SMSOTPService.get_cache_key(f"{SMS_CONFIG['ATTEMPTS_PREFIX']}_{otp_type}", phone_number)
        current_attempts = cache.get(cache_key, 0)
        new_attempts = current_attempts + 1
        
        # Set timeout = OTP expire time
        timeout = SMS_CONFIG['OTP_EXPIRE_MINUTES'] * 60
        cache.set(cache_key, new_attempts, timeout)
        
        return new_attempts
    
    @staticmethod
    def clear_otp_attempts(phone_number, otp_type):
        """Xóa số lần thử OTP"""
        cache_key = SMSOTPService.get_cache_key(f"{SMS_CONFIG['ATTEMPTS_PREFIX']}_{otp_type}", phone_number)
        cache.delete(cache_key)
    
    @staticmethod
    def store_otp(phone_number, otp_type, otp_code, user_data=None):
        """Lưu OTP vào cache"""
        cache_key = SMSOTPService.get_cache_key(f"{otp_type}_otp", phone_number)
        
        otp_data = {
            'otp': otp_code,
            'created_at': timezone.now().isoformat(),
            'phone_number': phone_number,
            'type': otp_type,
        }
        
        # Thêm user_data nếu có (cho trường hợp đăng ký)
        if user_data:
            otp_data['user_data'] = user_data
        
        timeout = SMS_CONFIG['OTP_EXPIRE_MINUTES'] * 60  # Convert to seconds
        cache.set(cache_key, otp_data, timeout)
          # Reset attempts counter
        SMSOTPService.clear_otp_attempts(phone_number, otp_type)
        
        return otp_data

    @staticmethod
    def verify_otp(phone_number, input_otp):
        """Xác thực OTP và trả về dữ liệu request đã lưu"""
        # Kiểm tra phone có bị block không
        if SMSOTPService.is_phone_blocked(phone_number):
            hours = SMS_CONFIG['PHONE_BLOCK_DURATION_HOURS']
            return {
                'success': False,
                'message': SMS_ERROR_MESSAGES['PHONE_BLOCKED'].format(hours=hours)
            }
        
        # Lấy OTP từ cache (chỉ có 1 pending request per phone)
        cache_key = SMSOTPService.get_cache_key("pending_request", phone_number)
        otp_data = cache.get(cache_key)
        
        if not otp_data:
            return {
                'success': False,
                'message': SMS_ERROR_MESSAGES['OTP_EXPIRED']
            }
        
        # Kiểm tra số lần thử (dùng pending_request làm type)
        attempts = SMSOTPService.get_otp_attempts(phone_number, "pending_request")
        if attempts >= SMS_CONFIG['OTP_MAX_ATTEMPTS']:
            # Xóa OTP và block phone nếu quá nhiều lần thất bại
            cache.delete(cache_key)
            SMSOTPService.block_phone(phone_number)
            return {
                'success': False,
                'message': SMS_ERROR_MESSAGES['OTP_MAX_ATTEMPTS'].format(
                    max_attempts=SMS_CONFIG['OTP_MAX_ATTEMPTS']
                )
            }
        
        # Kiểm tra OTP
        if otp_data['otp'] != input_otp:
            new_attempts = SMSOTPService.increment_otp_attempts(phone_number, "pending_request")
            remaining_attempts = SMS_CONFIG['OTP_MAX_ATTEMPTS'] - new_attempts
            
            if remaining_attempts <= 0:
                # Xóa OTP và block phone
                cache.delete(cache_key)
                SMSOTPService.block_phone(phone_number)
                return {
                    'success': False,
                    'message': SMS_ERROR_MESSAGES['OTP_MAX_ATTEMPTS'].format(
                        max_attempts=SMS_CONFIG['OTP_MAX_ATTEMPTS']
                    )
                }
            
            return {
                'success': False,
                'message': f"{SMS_ERROR_MESSAGES['OTP_INVALID']} Còn lại {remaining_attempts} lần thử."
            }
        
        # OTP đúng - xóa khỏi cache và clear attempts
        cache.delete(cache_key)
        SMSOTPService.clear_otp_attempts(phone_number, "pending_request")
        
        return {
            'success': True,
            'action_type': otp_data['action_type'],
            'request_data': otp_data['request_data']        }

    @staticmethod
    def send_otp(phone_number, action_type, request_data):
        """Gửi OTP và lưu request data"""
        # Kiểm tra phone có bị block không
        if SMSOTPService.is_phone_blocked(phone_number):
            hours = SMS_CONFIG['PHONE_BLOCK_DURATION_HOURS']
            return {
                'success': False,
                'message': SMS_ERROR_MESSAGES['PHONE_BLOCKED'].format(hours=hours)
            }
        
        # Kiểm tra cooldown
        if SMSOTPService.is_resend_cooldown_active(phone_number):
            seconds = SMS_CONFIG['OTP_RESEND_COOLDOWN_SECONDS']
            return {
                'success': False,
                'message': SMS_ERROR_MESSAGES['RESEND_COOLDOWN'].format(seconds=seconds)
            }
        
        # Tạo OTP
        otp_code = SMSOTPService.generate_otp()
        
        # Lưu OTP cùng với request data
        cache_key = SMSOTPService.get_cache_key("pending_request", phone_number)
        otp_data = {
            'otp': otp_code,
            'action_type': action_type,
            'request_data': request_data,
            'created_at': timezone.now().isoformat(),
            'phone_number': phone_number,
        }
        
        timeout = SMS_CONFIG['OTP_EXPIRE_MINUTES'] * 60  # Convert to seconds
        cache.set(cache_key, otp_data, timeout)
        
        # Reset attempts counter
        SMSOTPService.clear_otp_attempts(phone_number, "pending_request")
        
        # Set cooldown
        SMSOTPService.set_resend_cooldown(phone_number)
        
        # Mô phỏng gửi SMS
        sms_content = SMS_CONFIG['SMS_TEMPLATES'][action_type.upper()].format(
            otp=otp_code,
            expire_minutes=SMS_CONFIG['OTP_EXPIRE_MINUTES']
        )
        
        print(f"📱 [SMS SIMULATION] To: {phone_number}")
        print(f"📱 [SMS CONTENT] {sms_content}")
        
        return {
            'success': True,
            'message': f'Mã OTP đã được gửi đến số điện thoại {phone_number}',
            'otp_code': otp_code if SMS_CONFIG['SIMULATE_SMS'] else None,  # Chỉ trả về OTP khi mô phỏng
            'expires_in': SMS_CONFIG['OTP_EXPIRE_MINUTES'] * 60
        }
