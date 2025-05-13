import requests
from icecream import ic
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from account.models import CustomUser


def get_bot_id_from_token(token: str) -> int:
    response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
    ic(response.content)
    if response.ok:
        ic(response.ok)
        return response.json()["result"]["id"]
    raise ValueError("Invalid bot token")


class BotUserJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
            return CustomUser.objects.get(chat_id=user_id)
        except (KeyError, CustomUser.DoesNotExist):
            raise AuthenticationFailed("User not found or invalid token")
