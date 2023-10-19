""" test auth control flow """

import aiounittest
import datetime
import unittest
import aiohttp
import asyncio
from unittest.mock import AsyncMock
from mypermobil import MyPermobil



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

    async def test_battery_info(self) -> dict:
        """ test battery info """
        self.api.request_endpoint = AsyncMock(return_value={})

        return await self.api.get_battery_info()

    async def test_daily_usage(self) -> dict:
        """ test daily usage info """
        self.api.request_endpoint = AsyncMock(return_value={})

        return await self.api.get_daily_usage()

    async def test_records_info(self) -> dict:
        """ test records info """
        self.api.request_endpoint = AsyncMock(return_value={})

        return await self.api.get_usage_records()

    async def test_gps_info(self) -> dict:
        """ test gps info """
        self.api.request_endpoint = AsyncMock(return_value={})

        return await self.api.get_gps_position()


if __name__ == "__main__":
    unittest.main()
