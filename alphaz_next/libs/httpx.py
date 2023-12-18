# MODULES
import asyncio
import time
from typing import Any, List, Literal, Optional, Type, TypeVar, Union

# FASTAPI
from fastapi import HTTPException

# HTTPX
import httpx
from pydantic import BaseModel


def make_request_with_retry(
    method: Literal["POST", "PATCH", "PUT", "DELETE", "GET"],
    url,
    max_retries: int = 3,
    retry_on_status: Optional[List[int]] = None,
    timeout: Optional[float] = None,
    **kwargs,
) -> httpx.Response:
    """
    Makes an HTTP request with retries in case of a timeout error.

    Args:
        method (Literal["POST", "PATCH", "PUT", "DELETE", "GET"]): The HTTP method to use.
        url (str): The URL to make the request to.
        max_retries (int, optional): The maximum number of retries to attempt. Defaults to 3.
        retry_on_status (List[int], optional): A list of HTTP status codes to retry on. Defaults to None.
        timeout (float, optional): The timeout value for the request. Defaults to None.
        **kwargs: Additional keyword arguments to pass to the HTTP client.

    Returns:
        httpx.Response: The HTTP response.

    Raises:
        RuntimeError: If the maximum number of retries is exceeded or unknown error occurs.
    """
    item_repr = {
        "method": method,
        "url": url,
        "kwargs": kwargs,
    }

    retry_statuses = retry_on_status or []

    for retry_count in range(max_retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                response: httpx.Response = getattr(client, method.lower())(
                    url, **kwargs
                )
        except httpx.ReadTimeout as ex:
            if retry_count == max_retries:
                message = f"Unable to contact server after several retries {item_repr}"
                raise RuntimeError(message) from ex

            wait_time = 2**retry_count
            time.sleep(wait_time)
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code in retry_statuses and retry_count < max_retries:
                wait_time = 2**retry_count
                time.sleep(wait_time)
            else:
                raise ex
        except Exception as ex:
            message = "An unknown error occurs while contacting external server"
            raise RuntimeError(message) from ex
        else:
            return response

    raise RuntimeError("Maximum number of retries exceeded")


async def make_async_request_with_retry(
    method: Literal["POST", "PATCH", "PUT", "DELETE", "GET"],
    url: str,
    max_retries: int = 3,
    retry_on_status: Optional[List[int]] = None,
    timeout: Optional[float] = None,
    **kwargs,
) -> httpx.Response:
    """
    Makes an HTTP request with retries in case of a timeout error.

    Args:
        method (Literal["POST", "PATCH", "PUT", "DELETE", "GET"]): The HTTP method to use.
        url (str): The URL to make the request to.
        max_retries (int, optional): The maximum number of retries to attempt. Defaults to 3.
        retry_on_status (List[int], optional): A list of HTTP status codes to retry on. Defaults to None.
        timeout (float, optional): The timeout value for the request. Defaults to None.
        **kwargs: Additional keyword arguments to pass to the HTTP client.

    Returns:
        httpx.Response: The HTTP response.

    Raises:
        RuntimeError: If the maximum number of retries is exceeded or unknown error occurs.
    """
    item_repr = {
        "method": method,
        "url": url,
        "kwargs": kwargs,
    }

    retry_statuses = retry_on_status or []

    for retry_count in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response: httpx.Response = await getattr(client, method.lower())(
                    url, **kwargs
                )
        except httpx.ReadTimeout as ex:
            if retry_count == max_retries:
                message = f"Unable to contact server after several retries {item_repr}"
                raise RuntimeError(message) from ex

            wait_time = 2**retry_count
            await asyncio.sleep(wait_time)
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code in retry_statuses and retry_count < max_retries:
                wait_time = 2**retry_count
                await asyncio.sleep(wait_time)
            else:
                raise ex
        except Exception as ex:
            message = "An unknown error occurs while contacting external server"
            raise RuntimeError(message) from ex
        else:
            return response

    raise RuntimeError("Maximum number of retries exceeded")


'''
async def make_async_request_with_retry(
    method: Literal["POST", "PATCH", "PUT", "DELETE", "GET"],
    url,
    max_retries: int = 3,
    **kwargs,
) -> httpx.Response:
    """
    Makes an HTTP request with retries in case of a timeout error.

    Args:
        method (Literal["POST", "PATCH", "PUT", "DELETE", "GET"]): The HTTP method to use.
        url (str): The URL to make the request to.
        max_retries (int, optional): The maximum number of retries to attempt. Defaults to 3.
        **kwargs: Additional keyword arguments to pass to the HTTP client.

    Returns:
        httpx.Response: The HTTP response.

    Raises:
        RuntimeError: If the maximum number of retries is exceeded or unknown error occurs.
    """
    item_repr = {
        "method": method,
        "url": url,
        "kwargs": kwargs,
    }

    try:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await getattr(client, method.lower())(
                url, **kwargs
            )
    except httpx.ReadTimeout as ex:
        if max_retries == 0:
            message = f"Unable to contact server after several retries {item_repr}"
            raise RuntimeError(message) from ex

        max_retries -= 1
        return await make_async_request_with_retry(
            method=method,
            url=url,
            max_retries=max_retries,
            **kwargs,
        )
    except Exception as ex:
        message = "An unknown error occurs while contacting external server"
        raise RuntimeError(message) from ex

    return response


def sync(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))

    return wrapper


def make_request_with_retry(
    method: Literal["POST", "PATCH", "PUT", "DELETE", "GET"],
    url,
    max_retries: int = 3,
    **kwargs,
) -> httpx.Response:
    """
    Makes an HTTP request with retries in case of a timeout error.

    Args:
        method (Literal["POST", "PATCH", "PUT", "DELETE", "GET"]): The HTTP method to use.
        url (str): The URL to make the request to.
        max_retries (int, optional): The maximum number of retries to attempt. Defaults to 3.
        **kwargs: Additional keyword arguments to pass to the HTTP client.

    Returns:
        httpx.Response: The HTTP response.

    Raises:
        RuntimeError: If the maximum number of retries is exceeded or unknown error occurs.
    """
    item_repr = {
        "method": method,
        "url": url,
        "kwargs": kwargs,
    }

    try:
        with httpx.Client() as client:
            response: httpx.Response = getattr(client, method.lower())(url, **kwargs)
    except httpx.ReadTimeout as ex:
        if max_retries == 0:
            message = f"Unable to contact server after several retries {item_repr}"
            raise RuntimeError(message) from ex

        max_retries -= 1
        return make_request_with_retry(
            method=method,
            url=url,
            max_retries=max_retries,
            **kwargs,
        )
    except Exception as ex:
        message = "An unknown error occurs while contacting external server"
        raise RuntimeError(message) from ex

    return response
'''

T = TypeVar("T", bound=BaseModel)


def post_process_http_response(
    response: httpx.Response,
    schema: Type[T] = None,
    mode_alpha: bool = False,
) -> Union[T, List[T], Any]:
    """
    Processes an HTTP response and returns the response body as a validated object or a list of validated objects.

    Args:
        response: The HTTP response to process.
        schema: The schema to use for validating the response body.
        mode_alpha: Whether to use the "data" key in the response body for validation.

    Returns:
        The validated response body as an object or a list of objects.

    Raises:
        HTTPException: If the response is not a success.
    """
    if not response.is_success:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
            headers=response.headers,
        )

    response_json = response.json()
    if mode_alpha:
        response_json = response_json.get("data")

    if schema is None:
        return response_json

    if isinstance(response_json, (list, tuple)):
        return [schema.model_validate(item) for item in response_json]

    return schema.model_validate(response_json)
