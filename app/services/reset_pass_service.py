import secrets
from datetime import datetime, timedelta

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)  # 6 digit secure OTP


def get_expiry():
    return datetime.utcnow() + timedelta(minutes=10)