from rest_framework_simplejwt.tokens import AccessToken
from .models_access_blacklist import BlacklistedAccessToken
from django.http import JsonResponse
import logging

logger = logging.getLogger("django")

class AccessTokenBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.headers.get('Authorization', '')
        logger.info(f"[BlacklistMiddleware] Authorization header: {auth}")
        if auth.startswith('Bearer '):
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
                logger.warning(f"[BlacklistMiddleware] Exception: {e}")
        return self.get_response(request)
