from aiohttp import hdrs

from src.configs import ServiceCallerConfig
from src.errors import BadRequestError
from src.utils.http import Request


class OAuthService:
    @staticmethod
    def get_google_auth_url(redirect_uri: str) -> str:
        """
        Get Google authentication URL:

        Args:
            redirect_uri: Redirect URI

        Returns:
            str: Google authentication URL.
        """
        return (f"{ServiceCallerConfig.Google.AUTH_URI}?"
                f"client_id={ServiceCallerConfig.Google.CLIENT_ID}"
                f"&redirect_uri={redirect_uri}"
                f"&response_type=code"
                f"&scope=email%20profile%20openid"
                f"&access_type=offline&prompt=consent")

    @staticmethod
    async def call_google_auth_service(code: str, redirect_uri: str) -> dict:
        """
        Call Google authentication service:

        Args:
            code (str): Authorization code.
            redirect_uri: Redirect URI


        Returns:
            dict: Token response.
        """
        url = f"{ServiceCallerConfig.Google.TOKEN_URI}"
        payload = {
            "code": code,
            "client_id": ServiceCallerConfig.Google.CLIENT_ID,
            "client_secret": ServiceCallerConfig.Google.CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        headers = {hdrs.CONTENT_TYPE: "application/x-www-form-urlencoded"}
        response: Request = await Request(
            method=hdrs.METH_POST,
            url=url,
            data=payload,
            headers=headers,
            timeout=ServiceCallerConfig.Google.TIMEOUT,
        )
        if response.is_valid(raise_exception=False):
            return response.get_validated_data()
        else:
            raise BadRequestError("Invalid response from Google authentication service",
                                  detail=response.get_exception())

    @staticmethod
    async def call_google_user_service(token: str) -> dict:
        """
        Call Google user service:

        Args:
            token (str): Access token.

        Returns:
            dict: User response.
        """
        url = f"{ServiceCallerConfig.Google.USER_URI}"
        headers = {"Authorization": f"Bearer {token}"}

        response: Request = await Request(
            method=hdrs.METH_GET,
            url=url,
            headers=headers,
            timeout=ServiceCallerConfig.Google.TIMEOUT,
        )
        if response.is_valid(raise_exception=False):
            return response.get_validated_data()
        else:
            raise BadRequestError("Invalid response from Google user service",
                                  detail=response.get_exception())
