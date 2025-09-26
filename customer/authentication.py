# customer/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Customer
from rest_framework_simplejwt.exceptions import TokenError

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("JWT_TOKEN")
        if not token:
            return None

        try:
            validated_token = self.get_validated_token(token)
            # get user_id from token
            user_id = validated_token.get("user_id")
            # fetch Customer instead of default User
            customer = Customer.objects.filter(id=user_id).first()
            if not customer:
                return None
            return (customer, validated_token)
        except TokenError:
            return None
