""" test auth control flow """

import aiounittest
import datetime
import unittest
import asyncio
from unittest.mock import AsyncMock
from mypermobil import (
    MyPermobil,
    MyPermobilClientException,
    MyPermobilAPIException,
    BATTERY_AMPERE_HOURS_LEFT,
    RECORDS_DISTANCE,
    RECORDS_SEATING,
    ENDPOINT_VA_USAGE_RECORDS,
)


# pylint: disable=missing-docstring
class TestRequest(aiounittest.AsyncTestCase):
    def setUp(self):
        ttl = datetime.datetime.now() + datetime.timedelta(days=1)
        self.api = MyPermobil(
            "test",
            AsyncMock(),
            email="valid@email.com",
            region="http://example.com",
            code="123456",
            token="a" * 256,
            expiration_date=ttl.strftime("%Y-%m-%d"),
        )
        self.api.self_authenticate()

    async def test_request_item(self):
        resp = AsyncMock(status=200)
        resp.json = AsyncMock(return_value={BATTERY_AMPERE_HOURS_LEFT: 123})
        self.api.get_request = AsyncMock(return_value=resp)

        res = await self.api.request_item(BATTERY_AMPERE_HOURS_LEFT)

        assert res == 123
        assert self.api.get_request.call_count == 1

    async def test_request_item_404(self):
        status = 404
        msg = "not found"
        resp = AsyncMock(status=status)
        resp.json = AsyncMock(return_value={"error": msg})
        self.api.get_request = AsyncMock(return_value=resp)

        with self.assertRaises(MyPermobilAPIException) as err:
            await self.api.request_item(BATTERY_AMPERE_HOURS_LEFT)
            assert err.message == f"Permobil API {status}: {msg}"

    async def test_request_non_existent_item(self):
        item = "this item is not an item that exists"
        with self.assertRaises(MyPermobilClientException) as err:
            await self.api.request_item(item)
            assert err.message == f"No endpoint for item: {item}"

    async def test_request_non_existent_endpoint(self):
        endpoint = "this endpoint does not exist"
        item = "invalid item"
        with self.assertRaises(MyPermobilClientException) as err:
            await self.api.request_item(item, endpoint=endpoint)
            assert err.message == f"{item} not in endpoint {endpoint}"

    async def test_request_non_invalid_endpoint(self):
        endpoint = "this endpoint does not exist"
        item = RECORDS_SEATING
        with self.assertRaises(MyPermobilClientException) as err:
            await self.api.request_item(item, endpoint=endpoint)
            assert err.message == f"Invalid endpoint {endpoint}"

    async def test_request_request_endpoint_cache(self):
        """call the same endpoint twice and check that the cache is used"""
        resp = AsyncMock(status=200)
        resp.json = AsyncMock(
            return_value={RECORDS_DISTANCE: 123, RECORDS_SEATING: 456}
        )
        self.api.get_request = AsyncMock(return_value=resp)

        res1 = await self.api.request_item(RECORDS_DISTANCE)
        res2 = await self.api.request_item(RECORDS_SEATING)

        assert res1 == 123
        assert res2 == 456
        assert self.api.get_request.call_count == 1
        assert self.api.get_request.call_args[0][0].endswith(ENDPOINT_VA_USAGE_RECORDS)

    async def test_request_request_endpoint_async(self):
        """call the same endpoint twice and check that the cache is used"""

        async def delay():
            await asyncio.sleep(2)
            return {RECORDS_DISTANCE: 123, RECORDS_SEATING: 456}

        resp = AsyncMock(status=200)
        resp.json = AsyncMock(side_effect=delay)
        self.api.get_request = AsyncMock(return_value=resp)
        task1 = asyncio.create_task(self.api.request_item(RECORDS_DISTANCE))
        task2 = asyncio.create_task(self.api.request_item(RECORDS_SEATING))
        res1 = await task1
        res2 = await task2

        assert res1 == 123
        assert res2 == 456
        assert self.api.get_request.call_count == 1
        assert self.api.get_request.call_args[0][0].endswith(ENDPOINT_VA_USAGE_RECORDS)

    async def test_request_request_endpoint_cache_exception(self):
        status = 404
        msg = "not found"
        resp = AsyncMock(status=status)
        resp.json = AsyncMock(return_value={"error": msg})
        self.api.get_request = AsyncMock(return_value=resp)

        with self.assertRaises(MyPermobilAPIException) as err:
            await self.api.request_item(RECORDS_DISTANCE)
            assert err.message == f"Permobil API {status}: {msg}"
        with self.assertRaises(MyPermobilAPIException) as err:
            await self.api.request_item(RECORDS_SEATING)
            assert err.message == f"Permobil API {status}: {msg}"

        assert self.api.get_request.call_count == 1
        assert self.api.get_request.call_args[0][0].endswith(ENDPOINT_VA_USAGE_RECORDS)


if __name__ == "__main__":
    unittest.main()
