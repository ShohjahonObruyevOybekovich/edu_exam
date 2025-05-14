from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from decouple import config
from icecream import ic

from account.auth import TelegramAuthenticator, generate_secret_key
from account.utils import get_bot_id_from_token, BotUserJWTAuthentication
from account.models import CustomUser

class JWTtokenGenerator(APIView):
    """
    Exchange Telegram initData for JWT token (single bot version).
    """
    def post(self, request):
        init_data = request.data.get("init_data")
        if not init_data:
            raise ValidationError("'init_data' is required.")

        bot_token = config("BOT_TOKEN")
        if not bot_token:
            raise ValidationError("BOT_TOKEN is not configured.")

        try:
            secret_key = generate_secret_key(bot_token)
            authenticator = TelegramAuthenticator(secret=secret_key)
            bot_id = get_bot_id_from_token(bot_token)
            validated_data = authenticator.validate_third_party(init_data, bot_id)
            tg_user = validated_data.user
            ic("Parsed User:", tg_user)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not tg_user:
            return Response({"error": "User data missing."}, status=400)

        user, _ = CustomUser.objects.get_or_create(
            chat_id=tg_user.id,
            defaults={"full_name": f"{tg_user.first_name} {tg_user.last_name or ''}".strip()}
        )

        access = AccessToken.for_user(user)
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(access),
            "refresh": str(refresh)
        }, status=200)


class JWTtokenRefresh(APIView):
    """
    Refresh JWT token.
    """
    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response({"error": "Refresh token is required"}, status=400)

        try:
            refresh = RefreshToken(token)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class Me(APIView):
    """
    Returns authenticated user info.
    """
    authentication_classes = [BotUserJWTAuthentication]

    def get(self, request):
        user = request.user
        if not isinstance(user, CustomUser):
            return Response({"error": "Authentication failed."}, status=401)

        return Response({
            "id": user.id,
            "name": user.full_name,
            "chat_id": user.chat_id,
            "phone": user.phone,
        })
