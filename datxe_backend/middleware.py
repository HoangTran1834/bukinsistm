from rest_framework_simplejwt.tokens import AccessToken
from .models_access_blacklist import BlacklistedAccessToken
from django.http import JsonResponse
import logging

logger = logging.getLogger("django")

class AccessTokenBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Danh sách các endpoint được miễn kiểm tra blacklist
        # Những endpoint này không yêu cầu authentication hoặc cho phép truy cập công khai
        self.exempt_paths = [
            '/api/auth/login/',
            '/api/auth/signup/',
            '/api/auth/reset-password/',
            '/api/auth/verify/',
            '/api/schema/',
            '/api/docs/',
            '/api/redoc/',
            '/admin/',
            '/static/',
            '/media/',
            '/api/route/search/',  # Public route search
            '/api/route/schedules/',  # Public schedule view
        ]

    def __call__(self, request):
        # Kiểm tra nếu path hiện tại được miễn kiểm tra
        if any(request.path.startswith(path) for path in self.exempt_paths):
            logger.info(f"[BlacklistMiddleware] Path {request.path} is exempt from blacklist check")
            return self.get_response(request)
            
        # Chỉ kiểm tra blacklist nếu có Authorization header
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            # Không có token, cho phép request đi tiếp (sẽ được xử lý bởi authentication middleware khác)
            logger.info(f"[BlacklistMiddleware] No Bearer token found for {request.path}, skipping blacklist check")
            return self.get_response(request)
            
        logger.info(f"[BlacklistMiddleware] Authorization header: {auth}")
        token_str = auth.replace('Bearer ', '')
        try:
            token = AccessToken(token_str)
            jti = token['jti']
            logger.info(f"[BlacklistMiddleware] Access token jti: {jti}")
            if BlacklistedAccessToken.objects.filter(jti=jti).exists():
                logger.info(f"[BlacklistMiddleware] Token {jti} is blacklisted!")
                return JsonResponse({'detail': 'Access token is blacklisted.'}, status=401)
            else:
                logger.info(f"[BlacklistMiddleware] Token {jti} is NOT blacklisted.")
        except Exception as e:
            logger.warning(f"[BlacklistMiddleware] Exception parsing token: {e}")
            # Token không hợp lệ, nhưng không chặn ở đây - để authentication middleware xử lý
            
        return self.get_response(request)
