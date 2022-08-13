from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")

class Response(GenericModel, Generic[T]):
    message: Optional[str]
    isSuccess: Optional[bool]
    data: Optional[T] = {}