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
            email="valid@email.com",
        )

    async def test_set_email(self):
        email = "valid@email.com"
        self.api.set_email(email)
        self.assertEqual(self.api.email, email)

        email = "invalid"
        with self.assertRaises(MyPermobilClientException):
            self.api.set_email(email)

    async def test_set_region(self):
        region = "http://example.com"
        self.api.set_region(region)
        self.assertEqual(self.api.region, region)

    async def test_request_application_code(self):
        self.api.set_email("valid@email.com")
        self.api.set_region("http://example.com")
        resp = MagicMock(status=204)
        resp.text = AsyncMock(return_value="OK")
        self.api.post_request = AsyncMock(return_value=resp)
        await self.api.request_application_code()

    async def test_request_application_code_invalid_response(self):
        resp = MagicMock(status=400)
        resp.text = AsyncMock(return_value="Error")
        self.api.post_request = AsyncMock(return_value=resp)
        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_application_code(
                email="test@example.com",
                region="http://example.com",
                application="myapp",
            )

    async def test_request_application_token(self):
        resp = AsyncMock(status=200)
        resp.json = AsyncMock(return_value={"token": "mytoken"})
        self.api.post_request = AsyncMock(return_value=resp)
        result = await self.api.request_application_token(
            email="test@example.com", code="123123"
        )
        expected_date = datetime.datetime.now() + datetime.timedelta(days=365)
        self.assertEqual(result, ("mytoken", expected_date.strftime("%Y-%m-%d")))

    async def test_request_application_token_invalid_response(self):
        self.api.post_request = AsyncMock(return_value=MagicMock(status=403))
        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_application_token(
                email="test@example.com", code="123123"
            )


if __name__ == "__main__":
    unittest.main()
