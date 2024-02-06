# MODULES
from enum import Enum as _Enum
import json as _json
import re as _re
from pathlib import Path as _Path
from typing import (
    Any as _Any,
    Dict as _Dict,
    List as _List,
    Literal as _Literal,
    Optional as _Optional,
)

# DEEPDIFF
from deepdiff import DeepDiff as _DeepDiff

# UNITTEST
from unittest import (
    TestCase as _TestCase,
    IsolatedAsyncioTestCase as _IsolatedAsyncioTestCase,
)

# FASTAPI
from fastapi.testclient import TestClient as _TestClient

# PYDANTIC
from pydantic import BaseModel as _BaseModel, Field as _Field

# HTTPX
from httpx import Response as _Response
from httpx._types import (
    HeaderTypes as _HeaderTypes,
    QueryParamTypes as _QueryParamTypes,
)
from alphaz_next.core.constants import HeaderEnum as _HeaderEnum

# LIBS
from alphaz_next.libs.file_lib import (
    save_file as _save_file,
    save_json_file as _save_json_file,
    open_json_file as _open_json_file,
    open_file as _open_file,
)


class ExpectedResponse(_BaseModel):
    """
    Represents the expected response from an API request.

    Attributes:
        status_code (int): The HTTP status code of the response.
        data (Any, optional): The data payload of the response. Defaults to None.
        status_description (List[str], optional): The description of the response status. Defaults to an empty list.
        pagination (str, optional): The pagination information of the response. Defaults to None.
        warning (bool, optional): Indicates if there is a warning in the response. Defaults to None.
    """

    status_code: int
    data: _Optional[_Any] = _Field(default=None)
    status_description: _Optional[_List[str]] = _Field(default_factory=lambda: [])
    pagination: _Optional[str] = _Field(default=None)
    warning: _Optional[bool] = _Field(default=None)


class APiResponse(_BaseModel):
    """
    Represents an API response.

    Attributes:
        status_code (int): The status code of the response.
        data (Optional[Any]): The data returned by the API.
        headers (Dict): The headers of the response.
    """

    status_code: int
    data: _Optional[_Any]
    headers: _Dict


class ResponseFormatEnum(_Enum):
    """Enum class representing different response formats."""

    JSON = "json"
    BYTES = "bytes"
    NO_CONTENT = "no_content"


class _AlphaTest(_TestCase):
    __RESET_BEFORE_NEXT_TEST__: bool = False

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the test class by creating the app, initializing the client, and performing any necessary setup steps.
        """
        cls.app = cls.create_app()

        cls.client = _TestClient(cls.app)

        cls.enable_reset_before_next_test()

    @classmethod
    def enable_reset_before_next_test(cls):
        """
        Enable the reset before the next test.

        This method sets the __RESET_BEFORE_NEXT_TEST__ class variable to True,
        indicating that the reset operation should be performed before the next test.
        """
        cls.__RESET_BEFORE_NEXT_TEST__ = True

    @classmethod
    def disable_reset_before_next_test(cls):
        """
        Disable the reset before the next test.

        This method sets the __RESET_BEFORE_NEXT_TEST__ class variable to False,
        indicating that the reset operation should not be performed before the next test.
        """
        cls.__RESET_BEFORE_NEXT_TEST__ = False

    @classmethod
    def create_app(cls):
        """
        Creates an instance of the app.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError()

    @classmethod
    def get_ignored_keys(cls) -> _List[str]:
        """
        Returns a list of ignored keys.

        Returns:
            List[str]: A list of ignored keys.
        """
        return []

    def add_fake_headers(
        self,
        headers: dict,
        with_fake_token: bool = False,
        with_fake_api_key: bool = False,
    ):
        """
        Adds fake headers to the given headers dictionary.

        Args:
            headers (dict): The original headers dictionary.
            with_fake_token (bool): Flag indicating whether to add a fake token header.
            with_fake_api_key (bool): Flag indicating whether to add a fake API key header.

        Returns:
            dict: The updated headers dictionary with the fake headers added.
        """
        if headers is None:
            headers = {}

        if with_fake_token:
            headers.update(
                {"Authorization": "Bearer fake_jwt"},
            )

        if with_fake_api_key:
            headers.update(
                {"api_key": "fake_api_key"},
            )

        return headers

    def get_client(
        self,
        url: str,
        params: _Optional[_QueryParamTypes] = None,
        headers: _Optional[_HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: _Optional[_Path] = None,
    ):
        """
        Sends a GET request to the specified URL with optional parameters and headers.

        Args:
            url (str): The URL to send the GET request to.
            params (Optional[Union[Dict[str, Any], List[Tuple[str, Any]]]]): Optional parameters to include in the request.
            headers (Optional[Dict[str, str]]): Optional headers to include in the request.
            response_format (ResponseFormatEnum): The format in which the response should be returned. Defaults to JSON.
            with_fake_token (bool): Whether to include a fake token in the headers. Defaults to True.
            with_fake_api_key (bool): Whether to include a fake API key in the headers. Defaults to True.
            saved_path (Optional[Union[str, Path]]): Optional path to save the response data. Defaults to None.

        Returns:
            APiResponse: An object containing the response data, status code, and headers.
        """
        headers = self.add_fake_headers(
            headers=headers,
            with_fake_token=with_fake_token,
            with_fake_api_key=with_fake_api_key,
        )

        response = self.client.get(
            url,
            params=params,
            headers=headers,
        )

        status_code, data = self._post_process_response(
            response=response,
            response_format=response_format,
            saved_path=saved_path,
        )

        return APiResponse(
            status_code=status_code,
            data=data,
            headers=response.headers,
            header_status_description=response.headers.get(
                _HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(_HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(_HeaderEnum.WARNING.value),
        )

    def put_client(
        self,
        url: str,
        data=None,
        json: _Any = None,
        params: _Optional[_QueryParamTypes] = None,
        headers: _Optional[_HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: _Path = None,
    ):
        """
        Sends a PUT request to the specified URL with the given parameters.

        Args:
            url (str): The URL to send the request to.
            data: The data to send in the request body.
            json: The JSON data to send in the request body.
            params: The query parameters to include in the request URL.
            headers: The headers to include in the request.
            response_format (ResponseFormatEnum): The format of the response data.
            with_fake_token (bool): Whether to include a fake token in the request headers.
            with_fake_api_key (bool): Whether to include a fake API key in the request headers.
            saved_path: The path to save the response data.

        Returns:
            APiResponse: The API response object containing the status code, data, and headers.
        """
        headers = self.add_fake_headers(
            headers=headers,
            with_fake_token=with_fake_token,
            with_fake_api_key=with_fake_api_key,
        )

        response = self.client.put(
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
        )

        status_code, data = self._post_process_response(
            response=response,
            response_format=response_format,
            saved_path=saved_path,
        )

        return APiResponse(
            status_code=status_code,
            data=data,
            headers=response.headers,
            header_status_description=response.headers.get(
                _HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(_HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(_HeaderEnum.WARNING.value),
        )

    def patch_client(
        self,
        url: str,
        data=None,
        json: _Any = None,
        params: _Optional[_QueryParamTypes] = None,
        headers: _Optional[_HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: _Path = None,
    ):
        """
        Sends a PATCH request to the specified URL using the client.

        Args:
            url (str): The URL to send the PATCH request to.
            data: The data to send in the request body.
            json: The JSON data to send in the request body.
            params: The query parameters to include in the request.
            headers: The headers to include in the request.
            response_format (ResponseFormatEnum): The format of the response data.
            with_fake_token (bool): Whether to include a fake token in the headers.
            with_fake_api_key (bool): Whether to include a fake API key in the headers.
            saved_path (_Path): The path to save the response data to.

        Returns:
            APiResponse: The API response object containing the status code, data, headers, and other information.
        """
        headers = self.add_fake_headers(
            headers=headers,
            with_fake_token=with_fake_token,
            with_fake_api_key=with_fake_api_key,
        )

        response = self.client.patch(
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
        )

        status_code, data = self._post_process_response(
            response=response,
            response_format=response_format,
            saved_path=saved_path,
        )

        return APiResponse(
            status_code=status_code,
            data=data,
            headers=response.headers,
            header_status_description=response.headers.get(
                _HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(_HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(_HeaderEnum.WARNING.value),
        )

    def post_client(
        self,
        url: str,
        data=None,
        json: _Any = None,
        params: _Optional[_QueryParamTypes] = None,
        headers: _Optional[_HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: _Path = None,
    ):
        """
        Sends a POST request to the specified URL using the provided data, JSON payload, parameters, and headers.
        Optionally adds fake token and API key headers.
        Processes the response and returns an APiResponse object.

        Args:
            url (str): The URL to send the POST request to.
            data (Any, optional): The data to send as the request body. Defaults to None.
            json (Any, optional): The JSON payload to send as the request body. Defaults to None.
            params (Optional[QueryParamTypes], optional): The query parameters to include in the request. Defaults to None.
            headers (Optional[HeaderTypes], optional): The headers to include in the request. Defaults to None.
            response_format (ResponseFormatEnum, optional): The format of the response data. Defaults to ResponseFormatEnum.JSON.
            with_fake_token (bool, optional): Whether to include a fake token header. Defaults to True.
            with_fake_api_key (bool, optional): Whether to include a fake API key header. Defaults to True.
            saved_path (Path, optional): The path to save the response data to. Defaults to None.

        Returns:
            APiResponse: The response object containing the status code, data, and headers.
        """
        headers = self.add_fake_headers(
            headers=headers,
            with_fake_token=with_fake_token,
            with_fake_api_key=with_fake_api_key,
        )

        response = self.client.post(
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
        )

        status_code, data = self._post_process_response(
            response=response,
            response_format=response_format,
            saved_path=saved_path,
        )

        return APiResponse(
            status_code=status_code,
            data=data,
            headers=response.headers,
            header_status_description=response.headers.get(
                _HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(_HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(_HeaderEnum.WARNING.value),
        )

    def delete_client(
        self,
        url: str,
        params: dict = None,
        headers: _Optional[_HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: _Path = None,
    ):
        """
        Sends a DELETE request to the specified URL with optional parameters and headers.

        Args:
            url (str): The URL to send the DELETE request to.
            params (dict, optional): The parameters to include in the request. Defaults to None.
            headers (Optional[_HeaderTypes], optional): The headers to include in the request. Defaults to None.
            response_format (ResponseFormatEnum, optional): The format of the response. Defaults to ResponseFormatEnum.JSON.
            with_fake_token (bool, optional): Whether to include a fake token in the headers. Defaults to True.
            with_fake_api_key (bool, optional): Whether to include a fake API key in the headers. Defaults to True.
            saved_path (_Path, optional): The path to save the response data. Defaults to None.

        Returns:
            APiResponse: The API response object containing the status code, data, and headers.
        """
        headers = self.add_fake_headers(
            headers=headers,
            with_fake_token=with_fake_token,
            with_fake_api_key=with_fake_api_key,
        )

        response = self.client.delete(
            url,
            params=params,
            headers=headers,
        )

        status_code, data = self._post_process_response(
            response=response,
            response_format=response_format,
            saved_path=saved_path,
        )

        return APiResponse(
            status_code=status_code,
            data=data,
            headers=response.headers,
            header_status_description=response.headers.get(
                _HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(_HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(_HeaderEnum.WARNING.value),
        )

    def _post_process_response(
        self,
        response: _Response,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        saved_path: _Path = None,
    ):
        """
        Post-processes the response based on the specified format and saves it to a file if required.

        Args:
            response: The response object to be processed.
            response_format: The format in which the response should be processed (default: JSON).
            saved_path: The path where the processed response should be saved (default: None).

        Returns:
            The status code of the response and the processed data.
        """
        match response_format:
            case response_format.JSON:
                data = response.json()
                if saved_path is not None:
                    _save_json_file(saved_path, data)
            case response_format.BYTES:
                data = response.content
                if saved_path is not None:
                    _save_file(saved_path, data)
            case response_format.NO_CONTENT:
                data = None
            case _:
                raise ValueError(f"{response_format=} unknown")

        return response.status_code, data

    def assert_bytes_except_row(
        self,
        first: bytes,
        second: bytes,
        exception_row_prefix: bytes,
    ):
        """
        Asserts that two byte strings are equal, except for rows starting with the exception_row_prefix.

        Args:
            first (bytes): The first byte string to compare.
            second (bytes): The second byte string to compare.
            exception_row_prefix (bytes): The prefix indicating rows that should be skipped during comparison.

        Raises:
            AssertionError: If the byte strings are not equal, excluding rows starting with the exception_row_prefix.
            AssertionError: If the number of rows in the byte strings is different.
        """
        first = first.replace(b"\r\n", b"\n")
        second = second.replace(b"\r\n", b"\n")
        first_rows = first.split(b"\n")
        second_rows = second.split(b"\n")
        assert len(first_rows) == len(second_rows), "Rows count mismatch"
        for first_row, second_row in zip(first_rows, second_rows):
            if first_row.startswith(exception_row_prefix) or second_row.startswith(
                exception_row_prefix
            ):
                continue  # Skip rows starting with exception_row_prefix
            self.assertEqual(first_row, second_row)

    def assertDictEqualExceptKeys(
        self,
        dict1: dict,
        dict2: dict,
        ignored_keys: list[str] = None,
    ):
        """
        Asserts that two dictionaries are equal except for the specified keys.

        Args:
            dict1 (dict): The first dictionary to compare.
            dict2 (dict): The second dictionary to compare.
            ignored_keys (list[str], optional): A list of keys to ignore during comparison. Defaults to None.
        """
        if ignored_keys is None:
            ignored_keys = []

        dict1_filtered = {k: v for k, v in dict1.items() if k not in ignored_keys}
        dict2_filtered = {k: v for k, v in dict2.items() if k not in ignored_keys}
        self.assertDictEqual(dict1_filtered, dict2_filtered)

    def assertNestedDictEqual(
        self,
        first: _Dict,
        second: _Dict,
        ignored_keys: _List[str] = None,
    ):
        """
        Asserts that two nested dictionaries are equal, considering optional ignored keys.

        Args:
            first (dict): The first nested dictionary.
            second (dict): The second nested dictionary.
            ignored_keys (list[str], optional): A list of keys to be ignored during comparison. Defaults to None.

        Raises:
            AssertionError: If the dictionaries are not equal.

        """
        ignored_keys = [_re.compile(item) for item in ignored_keys or []]

        deep_diff = _DeepDiff(
            first,
            second,
            exclude_regex_paths=ignored_keys,
            ignore_numeric_type_changes=True,
        )

        assert not deep_diff, f"Dictionaries are not equal: {deep_diff}"

    def assertListOfDictEqual(
        self,
        first: _List[dict],
        second: _List[dict],
        ignored_keys: _List[str] = None,
    ):
        """
        Asserts that two lists of dictionaries are equal.

        Args:
            first (List[dict]): The first list of dictionaries.
            second (List[dict]): The second list of dictionaries.
            ignored_keys (List[str], optional): A list of keys to ignore during comparison. Defaults to None.
        """
        self.assertEqual(len(first), len(second))
        for dict1, dict2 in zip(first, second):
            self.assertNestedDictEqual(dict1, dict2, ignored_keys)

    def assertResponseEqual(
        self,
        expected_response: ExpectedResponse,
        response: APiResponse,
        ignore_keys: bool = True,
    ):
        """
        Asserts that the expected response matches the actual response.

        Args:
            expected_response (ExpectedResponse): The expected response object.
            response (APiResponse): The actual response object.
            ignore_keys (bool, optional): Whether to ignore certain keys during comparison. Defaults to True.
        """
        self.assertEqual(expected_response.status_code, response.status_code)

        self.assertEqual(
            expected_response.pagination,
            response.headers.get(_HeaderEnum.PAGINATION.value),
        )

        header_status_description = response.headers.get(
            _HeaderEnum.STATUS_DESCRIPTION.value, []
        )
        if isinstance(header_status_description, str):
            header_status_description = _json.loads(
                response.headers.get(_HeaderEnum.STATUS_DESCRIPTION.value)
            )

            if not isinstance(header_status_description, list):
                header_status_description = [header_status_description]

        self.assertEqual(
            expected_response.status_description,
            header_status_description,
        )

        expected_response_warning = None
        if expected_response.warning is not None:
            expected_response_warning = "1" if expected_response.warning else "0"

        self.assertEqual(
            expected_response_warning, response.headers.get(_HeaderEnum.WARNING.value)
        )

        if isinstance(expected_response.data, list):
            self.assertListOfDictEqual(
                expected_response.data,
                response.data,
                ignored_keys=self.get_ignored_keys() if ignore_keys else None,
            )
        elif isinstance(expected_response.data, dict):
            self.assertNestedDictEqual(
                expected_response.data,
                response.data,
                ignored_keys=self.get_ignored_keys() if ignore_keys else None,
            )
        else:
            self.assertEqual(
                expected_response.data,
                response.data,
            )


class AlphaTestCase(_AlphaTest):
    """
    Base test case class for Alpha project.
    """

    def setUp(self):
        """
        Set up the test environment before each test case.

        If the flag __RESET_BEFORE_NEXT_TEST__ is set to True, the method resets the tables.
        """
        if not self.__RESET_BEFORE_NEXT_TEST__:
            return

        self.reset_tables()

        self.__RESET_BEFORE_NEXT_TEST__ = False

    @classmethod
    def reset_tables(cls):
        """
        Resets the tables in the database.
        """
        raise NotImplementedError()


class AlphaIsolatedAsyncioTestCase(_IsolatedAsyncioTestCase, _AlphaTest):
    """A base test case class for asynchronous tests with Alpha-specific setup and teardown."""

    async def asyncSetUp(self):
        """
        Set up the test case asynchronously.

        If `__RESET_BEFORE_NEXT_TEST__` is True, reset the tables before each test.
        """
        if not self.__RESET_BEFORE_NEXT_TEST__:
            return

        await self.reset_tables()

        self.__RESET_BEFORE_NEXT_TEST__ = False

    @classmethod
    async def reset_tables(cls):
        """
        Reset the tables in the database.
        """
        raise NotImplementedError()


def load_expected_data(
    saved_dir_path: _Path = None,
    saved_file_path: str = None,
    format: _Literal["json", "txt"] = "json",
    encoding: str = "utf-8",
    reset_before_next_test: bool = False,
):
    """
    Decorator function that loads expected data from a file and passes it to the decorated test function.

    Args:
        saved_dir_path (_Path, optional): The directory path where the expected data file is located. Defaults to None.
        saved_file_path (str, optional): The file path of the expected data file. Defaults to None.
        format (Literal["json", "txt"], optional): The format of the expected data file. Defaults to "json".
        encoding (str, optional): The encoding of the expected data file. Defaults to "utf-8".
        reset_before_next_test (bool, optional): Flag indicating whether to reset before the next test. Defaults to False.

    Returns:
        The decorated test function.
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            class_name = self.__class__.__name__
            function_name = func.__name__

            if not isinstance(self, _AlphaTest):
                raise TypeError(
                    f"{self.__class__.__name__} must be instance of {_AlphaTest.__name__}"
                )

            (
                self.enable_reset_before_next_test()
                if reset_before_next_test
                else self.disable_reset_before_next_test()
            )

            if saved_dir_path is None:
                return func(self, *args, **kwargs)

            file_path = (
                saved_dir_path / f"{class_name}__{function_name}.{format}"
                if saved_file_path is None
                else saved_dir_path / saved_file_path
            )

            try:
                match format:
                    case "json":
                        expected_data = _open_json_file(file_path, encoding=encoding)
                    case "txt":
                        expected_data = _open_file(file_path, encoding=encoding)
                    case _:
                        expected_data = {}
            except FileNotFoundError | FileExistsError:
                expected_data = {}

            data = func(self, expected_data, file_path, *args, **kwargs)

            return data

        return wrapper

    return decorator
