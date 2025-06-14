import jwt
import os
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

class SupabaseJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization", "").split()

        if not auth or auth[0].lower() != "bearer" or len(auth) != 2:
            return None

        token = auth[1]
        try:
            payload = jwt.decode(
                token,
                key=SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            return (AnonymousUser(), None)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("JWT has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid Supabase JWT: {e}")
