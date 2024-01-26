# MODULES
from enum import Enum
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

# DEEPDIFF
from deepdiff import DeepDiff

# UNITTEST
from unittest import TestCase, IsolatedAsyncioTestCase

# FASTAPI
from fastapi.testclient import TestClient

# PYDANTIC
from pydantic import BaseModel, Field

# HTTPX
from httpx import Response
from httpx._types import HeaderTypes, QueryParamTypes
from alphaz_next.core.constants import HeaderEnum

# LIBS
from alphaz_next.libs.file_lib import (
    save_file,
    save_json_file,
    open_json_file,
    open_file,
)


class ExpectedResponse(BaseModel):
    status_code: int
    data: Optional[Any] = Field(default=None)
    status_description: Optional[List[str]] = Field(default_factory=lambda: [])
    pagination: Optional[str] = Field(default=None)
    warning: Optional[bool] = Field(default=None)


class APiResponse(BaseModel):
    status_code: int
    data: Optional[Any]
    headers: Dict


class ResponseFormatEnum(Enum):
    JSON = "json"
    BYTES = "bytes"
    NO_CONTENT = "no_content"


class _AlphaTest(TestCase):
    __RESET_BEFORE_NEXT_TEST__: bool = False

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = cls.create_app()

        cls.client = TestClient(cls.app)

        cls.check_reset_before_next_test()

    @classmethod
    def check_reset_before_next_test(cls):
        cls.__RESET_BEFORE_NEXT_TEST__ = True

    @classmethod
    def uncheck_reset_before_next_test(cls):
        cls.__RESET_BEFORE_NEXT_TEST__ = False

    @classmethod
    def create_app(cls):
        raise NotImplementedError()

    @classmethod
    def get_ignored_keys(cls) -> List[str]:
        return []

    def add_fake_headers(
        self,
        headers: dict,
        with_fake_token: bool = False,
        with_fake_api_key: bool = False,
    ):
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
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: Optional[Path] = None,
    ):
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
                HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(HeaderEnum.WARNING.value),
        )

    def put_client(
        self,
        url: str,
        data=None,
        json: Any = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: Path = None,
    ):
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
                HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(HeaderEnum.WARNING.value),
        )

    def patch_client(
        self,
        url: str,
        data=None,
        json: Any = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: Path = None,
    ):
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
                HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(HeaderEnum.WARNING.value),
        )

    def post_client(
        self,
        url: str,
        data=None,
        json: Any = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: Path = None,
    ):
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
                HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(HeaderEnum.WARNING.value),
        )

    def delete_client(
        self,
        url: str,
        params: dict = None,
        headers: Optional[HeaderTypes] = None,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        with_fake_token: bool = True,
        with_fake_api_key: bool = True,
        saved_path: Path = None,
    ):
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
                HeaderEnum.STATUS_DESCRIPTION.value
            ),
            header_pagination=response.headers.get(HeaderEnum.PAGINATION.value),
            header_warning=response.headers.get(HeaderEnum.WARNING.value),
        )

    def _post_process_response(
        self,
        response: Response,
        response_format: ResponseFormatEnum = ResponseFormatEnum.JSON,
        saved_path: Path = None,
    ):
        match response_format:
            case response_format.JSON:
                data = response.json()
                if saved_path is not None:
                    save_json_file(saved_path, data)
            case response_format.BYTES:
                data = response.content
                if saved_path is not None:
                    save_file(saved_path, data)
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
        """Asserts that two dictionaries are equal except for the specified keys."""
        if ignored_keys is None:
            ignored_keys = []

        dict1_filtered = {k: v for k, v in dict1.items() if k not in ignored_keys}
        dict2_filtered = {k: v for k, v in dict2.items() if k not in ignored_keys}
        self.assertDictEqual(dict1_filtered, dict2_filtered)

    def assertNestedDictEqual(
        self,
        first: Dict,
        second: Dict,
        ignored_keys: List[str] = None,
    ):
        ignored_keys = [re.compile(item) for item in ignored_keys or []]

        deep_diff = DeepDiff(
            first,
            second,
            exclude_regex_paths=ignored_keys,
            ignore_numeric_type_changes=True,
        )

        assert not deep_diff, f"Dictionaries are not equal: {deep_diff}"

    def assertListOfDictEqual(
        self,
        first: list[dict],
        second: list[dict],
        ignored_keys: List[str] = None,
    ):
        self.assertEqual(len(first), len(second))
        for dict1, dict2 in zip(first, second):
            self.assertNestedDictEqual(dict1, dict2, ignored_keys)

    def assertResponseEqual(
        self,
        expected_response: ExpectedResponse,
        response: APiResponse,
        ignore_keys: bool = True,
    ):
        self.assertEqual(expected_response.status_code, response.status_code)

        self.assertEqual(
            expected_response.pagination,
            response.headers.get(HeaderEnum.PAGINATION.value),
        )

        header_status_description = response.headers.get(
            HeaderEnum.STATUS_DESCRIPTION.value, []
        )
        if isinstance(header_status_description, str):
            header_status_description = json.loads(
                response.headers.get(HeaderEnum.STATUS_DESCRIPTION.value)
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
            expected_response_warning, response.headers.get(HeaderEnum.WARNING.value)
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
    def setUp(self):
        if not self.__RESET_BEFORE_NEXT_TEST__:
            return

        self.reset_tables()

        self.__RESET_BEFORE_NEXT_TEST__ = False

    @classmethod
    def reset_tables(cls):
        raise NotImplementedError()


class AlphaIsolatedAsyncioTestCase(IsolatedAsyncioTestCase, _AlphaTest):
    async def asyncSetUp(self):
        if not self.__RESET_BEFORE_NEXT_TEST__:
            return

        await self.reset_tables()

        self.__RESET_BEFORE_NEXT_TEST__ = False

    @classmethod
    async def reset_tables(cls):
        raise NotImplementedError()


def load_expected_data(
    saved_dir_path: Path = None,
    saved_file_path: str = None,
    format: Literal["json", "txt"] = "json",
    encoding: str = "utf-8",
    reset_before_next_test: bool = False,
):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            class_name = self.__class__.__name__
            function_name = func.__name__

            if not isinstance(self, _AlphaTest):
                raise TypeError(
                    f"{self.__class__.__name__} must be instance of {_AlphaTest.__name__}"
                )

            self.check_reset_before_next_test() if reset_before_next_test else self.uncheck_reset_before_next_test()

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
                        expected_data = open_json_file(file_path, encoding=encoding)
                    case "txt":
                        expected_data = open_file(file_path, encoding=encoding)
                    case _:
                        expected_data = {}
            except FileNotFoundError | FileExistsError:
                expected_data = {}

            data = func(self, expected_data, file_path, *args, **kwargs)

            return data

        return wrapper

    return decorator
