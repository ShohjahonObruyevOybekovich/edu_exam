import json
from hmac import HMAC
import hashlib
from urllib.parse import parse_qsl
from collections import OrderedDict

class TelegramAuthenticator:
    def __init__(self, secret: bytes):
        self.secret = secret

    def validate_third_party(self, init_data: str, bot_id: int):
        parsed = OrderedDict(parse_qsl(init_data, keep_blank_values=True))
        hash_received = parsed.pop("hash", None)

        # ⚠️ At this point, 'user' is still a string — DO NOT decode yet
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        calculated_hash = HMAC(self.secret, data_check_string.encode(), hashlib.sha256).hexdigest()

        if hash_received != calculated_hash:
            raise ValueError("Hash verification failed.")

        # ✅ Now safely decode JSON fields
        if "user" in parsed:
            parsed["user"] = json.loads(parsed["user"])

        from .web_app.data import WebAppInitData
        return WebAppInitData(**parsed)


def generate_secret_key(bot_token: str) -> bytes:
    return hashlib.sha256(bot_token.encode()).digest()
