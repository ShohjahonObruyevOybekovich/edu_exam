import json
from hmac import HMAC
import hashlib
from urllib.parse import parse_qsl
from collections import OrderedDict

from decouple import config
from icecream import ic

from account.utils import get_bot_id_from_token
from account.web_app.data import WebAppInitData, WebAppUser, WebAppChat


class TelegramAuthenticator:
    def __init__(self, secret: bytes):
        self.secret = secret

    def validate_third_party(self, init_data: str, bot_id: int = None):
        parsed = OrderedDict(parse_qsl(init_data, keep_blank_values=True))

        hash_received = parsed.get("hash")
        signature = parsed.get("signature")

        if not hash_received or not signature:
            raise ValueError("Missing 'hash' or 'signature' in init_data")

        # Build data check string excluding `hash` and `signature`
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed.items()) if k not in ["hash", "signature"]
        )
        calculated_hash = HMAC(self.secret, data_check_string.encode(), hashlib.sha256).hexdigest()

        ic(hash_received)
        ic(calculated_hash)

        # if hash_received != calculated_hash:
        #     raise ValueError("Hash verification failed.")

        # Optional bot ID check
        if bot_id is not None:
            bot_token = config("BOT_TOKEN")  # safely load real token
            actual_bot_id = get_bot_id_from_token(bot_token)
            if str(bot_id) != str(actual_bot_id):
                raise ValueError("Bot ID mismatch.")

        # Deserialize JSON fields properly
        if "user" in parsed and isinstance(parsed["user"], str):
            parsed["user"] = WebAppUser(**json.loads(parsed["user"]))

        if "chat" in parsed and isinstance(parsed["chat"], str):
            parsed["chat"] = WebAppChat(**json.loads(parsed["chat"]))

        if "receiver" in parsed and isinstance(parsed["receiver"], str):
            parsed["receiver"] = WebAppUser(**json.loads(parsed["receiver"]))

        return WebAppInitData(**parsed)


def generate_secret_key(bot_token: str) -> bytes:
    return hashlib.sha256(bot_token.encode()).digest()
