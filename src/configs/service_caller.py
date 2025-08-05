import os
from dotenv import load_dotenv

load_dotenv()


class ServiceCallerConfig:
    class Optimizer:
        URI = os.environ.get('SERVICE_CALLER_OPTIMIZER_URI', 'http://algorithm:8001')
        OPTIMIZE_ENDPOINT = "/optimizer/optimize"
        HEALTH_ENDPOINT = "/health"
        TIMEOUT = 30

    class Google:
        AUTH_URI = os.environ.get('SERVICE_CALLER_GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth')
        TOKEN_URI = os.environ.get('SERVICE_CALLER_GOOGLE_URI', 'https://oauth2.googleapis.com/token')
        USER_URI = os.environ.get('SERVICE_CALLER_GOOGLE_USER_INFO_URI',
                                  'https://www.googleapis.com/oauth2/v1/userinfo')
        REDIRECT_LOGIN_URI = os.environ.get('SERVICE_CALLER_GOOGLE_REDIRECT_LOGIN_URI',
                                            "http://localhost:3000/callback/login")
        REDIRECT_REGISTER_URI = os.environ.get('SERVICE_CALLER_GOOGLE_REDIRECT_REGISTER_URI',
                                               "http://localhost:3000/callback/register")

        CLIENT_ID = os.environ.get('SERVICE_CALLER_GOOGLE_CLIENT_ID')
        CLIENT_SECRET = os.environ.get('SERVICE_CALLER_GOOGLE_CLIENT_SECRET')

        TIMEOUT = 30
