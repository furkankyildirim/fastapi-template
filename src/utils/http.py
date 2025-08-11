from __future__ import annotations
from contextvars import ContextVar

import json
from loguru import logger
from typing import AsyncContextManager, Type, Callable, Dict, Union, Any
from aiohttp import ClientSession, ClientResponse, hdrs, FormData
from pydantic import BaseModel

from .error import Error
from .common import json_serializer

request_id_trace_context = ContextVar("request_id_trace_context")

class HttpClient:
    session: ClientSession = None
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    @staticmethod
    async def start(
            *args,
            headers=None,
            json_serialize=json_serializer,
            raise_for_status=True,
            **kwargs
    ):
        if headers is None:
            headers = HttpClient.headers

        HttpClient.session = ClientSession(headers=headers,
                                           json_serialize=json_serialize,
                                           raise_for_status=raise_for_status,
                                           **kwargs)

    @staticmethod
    async def stop():
        await HttpClient.session.close()
        HttpClient.session = None

    @staticmethod
    async def restart(*args, **kwargs):
        await HttpClient.stop()
        await HttpClient.start(*args, **kwargs)

    def __call__(self) -> ClientSession:
        assert HttpClient.session is not None, "Session not found. Please start or restart session."
        return HttpClient.session


client = HttpClient()


class Request:
    """
        Response class
        - Makes requests without context manager
        - Silently handles exceptions during client call
        - Supports file uploads via multipart/form-data

        Attributes:
            request (Awaitable[ClientResponse]): Client request coroutine to be used to make request.
            validation_function (Callable): Validation function to be used after response received
            validation_model (BaseModel): Pydantic validation model to be used after response received
            validate_key (str): Key to be validated after response received. Ex. response["warehouse"]
            error_class (Error): Error class to wrap builtin Exceptions
            _response (Dict): Response object returned from request
            _validated_data (Dict): Data after validation and serialization of response object.
            _exception (Error): Wrapped exception object if any thrown during steps: request, validation, serialization
            
        File Upload Format:
            files (Dict): Dictionary with file information in format:
                {
                    'field_name': {
                        'filename': 'file.txt',
                        'content': b'file_content',
                        'content_type': 'text/plain'
                    }
                }
    """

    validation_function = None
    validation_model = None
    error_class = None

    def __init__(self,
                 method: hdrs.METH_ALL,
                 url: str,
                 *,
                 validation_function: Callable = None,
                 validation_model: Union[BaseModel, Type] = None,
                 validate_key: str = None,
                 error_class: Type[Error] = Error,
                 is_multipart: bool = False,
                 **kwargs):
        self.request = self._create_request(method, url, is_multipart, **kwargs)
        self.validation_function = validation_function
        self.validation_model = validation_model
        self.validate_key = validate_key
        self.is_multipart = is_multipart
        self.error_class: Type[Error] = error_class
        self._response: Union[Dict, None] = None
        self._validated_data = None
        self._exception: Union[Error, None] = None

    def _create_request(self, method: hdrs.METH_ALL,
                        url: str, is_multipart: bool = False,
                        raise_for_status: bool = False,
                        **kwargs) -> AsyncContextManager[ClientResponse]:
        """
            Internal request function to assigns aiohttp.ClientRequest to self.request

        Args:
            method (str): Request method to use ex: POST
            url (str): Request URL
            is_multipart (bool): When true, the request is a multipart/form-data request
            raise_for_status (bool): When true skips response parsing if status code >= 400
            **kwargs: Rest of aiohttp request kwargs including:
                - data: Form data or JSON data
                - files: Dictionary with file information for multipart uploads
                - headers: Request headers
                - timeout: Request timeout

        Returns:
            (AsyncContextManager[ClientResponse]): aiohttp request coroutine

        """
        self._request_info = {
            "method": method,
            "url": url,
            "data": kwargs.get('data'),
            "json": kwargs.get('json'),
            "files": kwargs.get('files')
        }

        headers = kwargs.pop('headers', {})
        data = kwargs.pop('data', None)
        files = kwargs.pop('files', None)
    
        request_id = request_id_trace_context.get(None)
        if request_id:
            headers["requestid"] = request_id
        
        if files or is_multipart:
            form_data = FormData()

            for key, value in data.items():
                # If value is a dict/list, convert to JSON string
                if isinstance(value, (dict, list)):
                    form_data.add_field(key, json.dumps(value), content_type='application/json')
                else:
                    form_data.add_field(key, str(value))
            
            # Add files if provided
            if files:
                for key, file_info in files.items():
                    if isinstance(file_info, dict):
                        filename = file_info.get('filename', 'file')
                        content = file_info.get('content', b'')
                        content_type = file_info.get('content_type', 'application/octet-stream')
                        form_data.add_field(key, content, filename=filename, content_type=content_type)
                    elif isinstance(file_info, tuple) and len(file_info) >= 2:
                        filename = file_info[0]
                        content = file_info[1]
                        content_type = file_info[2] if len(file_info) > 2 else 'application/octet-stream'
                        form_data.add_field(key, content, filename=filename, content_type=content_type)
                
            form_data_headers = form_data._gen_form_data().headers
            for key, value in form_data_headers.items():
                headers[key] = value

            data = form_data
            
        return client().request(method.upper(), url, raise_for_status=raise_for_status, headers=headers, data=data, **kwargs)

    async def __execute(self) -> Request:
        """
            Internal execute function to make request, validate and serialize
        Returns:
            (Response) - Self
        """

        self._response = None
        self._validated_data = None
        self._exception = None
        status = None
        try:

            # Make client call
            async with self.request as client_response:
                status = client_response.status

                # Parse response. Defaults json()
                await self._parse_response(client_response)

                # Handle http error status codes after response is set
                # Only runs if raise_for_status explicitly set to False on request
                if 400 <= status:
                    client_response.raise_for_status()

                # Validate response
                self._validate_response()
        except Exception:
            # Catch any exceptions thrown and wrap it with given Error class
            self._exception = self.error_class(
                detail={
                    "request": self._request_info,
                    "response": {
                        "status": status,
                        "data": self._response
                    }
                })
            # TODO: .with_current_traceback()

        return self

    async def _parse_response(self, client_response: ClientResponse) -> None:
        """
        Parses response with json() and assigns to self._response

        Args:
            client_response (ClientResponse): Response received from http client

        """
        try:
            self._response = await client_response.json()
        except Exception:
            # Before raising the actual exception, keep raw text response to log later.
            self._response = await client_response.text(errors="ignore")
            raise

    def _validate_response(self) -> None:
        """
            Validates response with given validation function and assigns to self._validated_response
        """
        response = self._response
        if self.validate_key:
            response = response[self.validate_key]

        # Validate with function if there is a validation function
        if self.validation_function:
            self._validated_data = self.validation_function(response)

        # Check if validation is a pydantic model
        elif self.validation_model:
            # If model has builtin parse_obj function, use it to validate
            if hasattr(self.validation_model, 'parse_obj'):
                self._validated_data = self.validation_model.model_validate(response)
            # Validate generic types
            else:
                self._validated_data = self.validation_model.model_validate(response)
        # Skip validation and return response as validated data
        else:
            self._validated_data = response

    def is_valid(self, raise_exception=False) -> bool:
        """
        Returns if data is validated without any exceptions.

        Args:
            raise_exception (bool): If true raises exception which was caught during client call

        Returns:
            (bool) - is_valid

        """

        if self.has_exception():
            if raise_exception:
                self.raise_exception()
            else:
                return False
        else:
            return True

    def get_response(self) -> Union[Dict, None]:
        """
            Returns original response returned from client call

        Returns:
            (Dict) - Parsed response object returned from client call
        """
        return self._response

    def get_validated_data(self) -> Any:
        """
           Returns validated data after passed through validation function/model

        Returns:
           Data object returned after validations.
        """
        return self._validated_data

    def get_exception(self) -> Union[Error, None]:
        """
           Accessor for _exception

        Returns:
           (Error) - Error object wrapped during client call
        """
        return self._exception

    def has_exception(self) -> bool:
        """
           Returns True if any exception caught during client call

        Returns:
           (bool)
        """
        return self._exception is not None

    def get_original_exception(self) -> Union[Exception, None]:
        """
           Returns original exception before wrapped with Error class

        Returns:
           (Exception) - Exception thrown during client call
        """
        return self._exception and self._exception.caught_exception

    def log_exception(self):
        """
        Logs caught exception

        """
        logger.opt(exception=self._exception).error(self._exception.message)
        # TODO: .with_current_traceback()

    def raise_exception(self, detail: Dict = None, log: bool = True):
        """
        Raises caught exception during client call

        Args:
            detail (Dict): Additional details to pass to exception. Used mainly for logging
            log (bool): When True logs exception

        Raises:
            error (Error): Exception wrapped with error class

        """
        if self._exception:
            if detail:
                self._exception.detail.update(detail)
            if log:
                self.log_exception()
            raise self.get_exception()

    def __await__(self):
        return self.__execute().__await__()