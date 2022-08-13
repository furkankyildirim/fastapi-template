from .router import Router
from src.controllers import UserController, AuthenticationController

user_route = Router(router=UserController.router, prefix='/api/user')
authentication_route = Router(router=AuthenticationController.router, prefix='/api/authentication')

__all__ = [
    "user_route",
    "authentication_route",
]
