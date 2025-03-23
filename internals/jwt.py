import jwt
import time
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_KEY")

def generate_access_token(userid):
    return jwt.encode(
        {
            "userid": userid,
            "exp": int(time.time()) + 300
        },
        SECRET_KEY.encode("utf-8"),
        algorithm="HS256"
    )

def generate_refresh_token(userid, token_version):
    return jwt.encode(
        {
            "userid": userid,
            "exp": int(time.time()) + 604800,
            "token_version": token_version
        },
        REFRESH_SECRET_KEY.encode("utf-8"),
        algorithm="HS256"
    )

def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return "expired"
    except jwt.InvalidTokenError:
        return "invalid"