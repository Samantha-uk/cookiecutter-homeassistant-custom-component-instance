"""Tests for Cookiecutter Home Assistant Custom Component Instance api."""
import asyncio

import aiohttp
from custom_components.cookiecutter_homeassistant_custom_component_instance.api import (
    CookiecutterHomeassistantCustomComponentInstanceApiClient,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession


async def test_api(hass, aioclient_mock, caplog):
    """Test API calls."""

    # To test the api submodule, we first create an instance of our API client
    api = CookiecutterHomeassistantCustomComponentInstanceApiClient(
        "test", "test", async_get_clientsession(hass)
    )

    # We then try a call to `async_get_data` after mocking the response. This is useful
    # for testing any logic that lives within the function, e.g. parsing or validating
    # the return data
    aioclient_mock.get(
        "https://jsonplaceholder.typicode.com/posts/1", json={"test": "test"}
    )
    assert await api.async_get_data() == {"test": "test"}

    # We do the same for `async_set_title`. Note the difference in the mock call
    # between the previous step and this one. We use `patch` here instead of `get`
    # because we know that `async_set_title` calls `api_wrapper` with `patch` as the
    # first parameter
    aioclient_mock.patch("https://jsonplaceholder.typicode.com/posts/1")
    assert await api.async_set_title("test") is None

    # In order to get 100% coverage, we need to test `api_wrapper` to test the code
    # that isn't already called by `async_get_data` and `async_set_title`. Because the
    # only logic that lives inside `api_wrapper` that is not being handled by a third
    # party library (aiohttp) is the exception handling, we also want to simulate
    # raising the exceptions to ensure that the function handles them as expected.
    caplog.clear()
    aioclient_mock.put(
        "https://jsonplaceholder.typicode.com/posts/1", exc=asyncio.TimeoutError
    )
    assert (
        await api.api_wrapper("put", "https://jsonplaceholder.typicode.com/posts/1")
        is None
    )
    assert (
        len(caplog.record_tuples) == 1
        and "Timeout error fetching information from" in caplog.record_tuples[0][2]
    )

    caplog.clear()
    aioclient_mock.post(
        "https://jsonplaceholder.typicode.com/posts/1", exc=aiohttp.ClientError
    )
    assert (
        await api.api_wrapper("post", "https://jsonplaceholder.typicode.com/posts/1")
        is None
    )
    assert (
        len(caplog.record_tuples) == 1
        and "Error fetching information from" in caplog.record_tuples[0][2]
    )

    caplog.clear()
    aioclient_mock.post("https://jsonplaceholder.typicode.com/posts/2", exc=Exception)
    assert (
        await api.api_wrapper("post", "https://jsonplaceholder.typicode.com/posts/2")
        is None
    )
    assert (
        len(caplog.record_tuples) == 1
        and "Something really wrong happened!" in caplog.record_tuples[0][2]
    )

    caplog.clear()
    aioclient_mock.post("https://jsonplaceholder.typicode.com/posts/3", exc=TypeError)
    assert (
        await api.api_wrapper("post", "https://jsonplaceholder.typicode.com/posts/3")
        is None
    )
    assert (
        len(caplog.record_tuples) == 1
        and "Error parsing information from" in caplog.record_tuples[0][2]
    )
