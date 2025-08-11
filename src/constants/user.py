from enum import StrEnum


class UserConstant:
    class Role(StrEnum):
        USER = 'user'
        ADMIN = 'admin'

    class Subscription(StrEnum):
        FREE = 'free'
        BASIC = 'basic'
        ADVANCED = 'advanced'
