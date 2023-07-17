""" test auth control flow """

import aiounittest
import datetime
import unittest
import aiohttp
import asyncio
from unittest.mock import AsyncMock
from mypermobil import (
    MyPermobil,
    MyPermobilClientException,
    MyPermobilAPIException,
    MyPermobilConnectionException,
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
        resp.json = AsyncMock(return_value={BATTERY_AMPERE_HOURS_LEFT[0]: 123})
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

        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_item(BATTERY_AMPERE_HOURS_LEFT)

    async def test_request_non_existent_item(self):
        item = "this item is not an item that exists"
        with self.assertRaises(MyPermobilClientException):
            await self.api.request_item(item)

    async def test_request_empty_item(self):
        item = []
        with self.assertRaises(MyPermobilClientException):
            await self.api.request_item(item)

    async def test_request_invalid_item(self):
        # scenario one, a list that does not have enough items
        items = [100]
        # mock request endpoint result
        resp = [1, 2, 3]
        self.api.request_endpoint = AsyncMock(return_value=resp)
        with self.assertRaises(MyPermobilClientException):
            await self.api.request_item(items, endpoint="test")

        # scenario two, dict that does not have specific item
        item = "i want this item"
        items = [item]
        # mock request endpoint result
        resp = {"i only have this item": 123}
        self.api.request_endpoint = AsyncMock(return_value=resp)
        with self.assertRaises(MyPermobilClientException):
            await self.api.request_item(items, endpoint="test")

    async def test_request_endpoint_ContentTypeError(self):
        # scenario one, a list that does not have enough items
        resp = AsyncMock(status=400)
        mock = AsyncMock()
        resp.json = AsyncMock(
            side_effect=aiohttp.client_exceptions.ContentTypeError(mock, mock)
        )
        self.api.get_request = AsyncMock(return_value=resp)
        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_endpoint("endpoint")

    #    async def test_request_non_existent_endpoint(self):
    #        endpoint = "this endpoint does not exist"
    #        item = "invalid item"
    #        with self.assertRaises(MyPermobilClientException):
    #            await self.api.request_item(item, endpoint=endpoint)

    #    async def test_request_non_invalid_endpoint(self):
    #        endpoint = "this endpoint does not exist"
    #        item = RECORDS_SEATING
    #        with self.assertRaises(MyPermobilClientException):
    #            await self.api.request_item(item, endpoint=endpoint)

    async def test_request_request_endpoint_cache(self):
        """call the same endpoint twice and check that the cache is used"""
        resp = AsyncMock(status=200)
        resp.json = AsyncMock(
            return_value={RECORDS_DISTANCE[0]: 123, RECORDS_SEATING[0]: 456}
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
            await asyncio.sleep(0.5)
            return {RECORDS_DISTANCE[0]: 123, RECORDS_SEATING[0]: 456}

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

        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_item(RECORDS_DISTANCE)
        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_item(RECORDS_SEATING)

        assert self.api.get_request.call_count == 1
        assert self.api.get_request.call_args[0][0].endswith(ENDPOINT_VA_USAGE_RECORDS)

    async def test_request_get_request(self):
        session = AsyncMock(status=200)
        session.get = AsyncMock(return_value=AsyncMock(status=200))
        self.api.session = session

        res = await self.api.get_request("http://example.com")
        assert res.status == 200

    async def test_request_get_request_exceptions(self):
        session = AsyncMock()
        mock = AsyncMock()
        session.get = AsyncMock(side_effect=aiohttp.ClientConnectorError(mock, mock))
        self.api.session = session
        with self.assertRaises(MyPermobilConnectionException):
            await self.api.get_request("http://example.com")

        session = AsyncMock()
        session.get = AsyncMock(side_effect=asyncio.TimeoutError())
        self.api.session = session
        with self.assertRaises(MyPermobilConnectionException):
            await self.api.get_request("http://example.com")

        session = AsyncMock()
        session.get = AsyncMock(side_effect=aiohttp.ClientError(None, None))
        self.api.session = session
        with self.assertRaises(MyPermobilConnectionException):
            await self.api.get_request("http://example.com")

        session = AsyncMock()
        session.get = AsyncMock(side_effect=ValueError())
        self.api.session = session
        with self.assertRaises(MyPermobilAPIException):
            await self.api.get_request("http://example.com")

    async def test_request_post_request_exceptions(self):
        session = AsyncMock()
        mock = AsyncMock()
        session.post = AsyncMock(side_effect=aiohttp.ClientConnectorError(mock, mock))
        self.api.session = session
        with self.assertRaises(MyPermobilConnectionException):
            await self.api.post_request("http://example.com")

        session = AsyncMock()
        session.post = AsyncMock(side_effect=asyncio.TimeoutError())
        self.api.session = session
        with self.assertRaises(MyPermobilConnectionException):
            await self.api.post_request("http://example.com")

        session = AsyncMock()
        session.post = AsyncMock(side_effect=aiohttp.ClientError(None, None))
        self.api.session = session
        with self.assertRaises(MyPermobilConnectionException):
            await self.api.post_request("http://example.com")

        session = AsyncMock()
        session.post = AsyncMock(side_effect=ValueError())
        self.api.session = session
        with self.assertRaises(MyPermobilAPIException):
            await self.api.post_request("http://example.com")

    async def test_request_product_id(self):
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
        response = [{"_id": "123"}]
        request_endpoint_mock = AsyncMock(return_value=response)
        self.api.request_endpoint = request_endpoint_mock

        await self.api.request_product_id()

        # test for the places it can fail
        # list is not length 1
        response = [{"_id": "123"}, {"_id": "123"}, {"_id": "123"}]
        request_endpoint_mock = AsyncMock(return_value=response)
        self.api.request_endpoint = request_endpoint_mock

        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_product_id()

        # response it not a list
        response = "not a list"
        request_endpoint_mock = AsyncMock(return_value=response)
        self.api.request_endpoint = request_endpoint_mock

        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_product_id()


if __name__ == "__main__":
    unittest.main()
