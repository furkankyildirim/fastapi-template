from .router import Router
from src.controllers import UserController, AuthController

auth_route = Router(router=AuthController.router, prefix='/auth')
user_route = Router(router=UserController.router, prefix='/user')


__all__ = [
    "auth_route",
    "user_route",
]
