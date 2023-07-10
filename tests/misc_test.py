""" test auth control flow """

import aiounittest
import datetime
import unittest
from unittest.mock import MagicMock, AsyncMock
from mypermobil import MyPermobil, MyPermobilClientException, MyPermobilAPIException


# pylint: disable=missing-docstring
class TestAuth(aiounittest.AsyncTestCase):
    def setUp(self):
        self.api = MyPermobil(
            "test",
            AsyncMock(),
            region="http://example.com",
        )

    def test_str(self):
        x = str(self.api)
        assert x

    async def test_close_session(self):
        await self.api.close_session()
        assert self.api.session is None

        with self.assertRaises(MyPermobilClientException):
            await self.api.close_session()


if __name__ == "__main__":
    unittest.main()
