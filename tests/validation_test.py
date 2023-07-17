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
            "",
            AsyncMock(),
        )

    async def test_set_email(self):
        email = "valid@email.com"
        self.api.set_email(email)
        self.assertEqual(self.api.email, email)

        email = "invalid"
        with self.assertRaises(MyPermobilClientException):
            self.api.set_email(email)

        email = ""
        with self.assertRaises(MyPermobilClientException):
            self.api.set_email(email)

    async def test_set_expiration_date(self):
        date = datetime.datetime.now() + datetime.timedelta(days=1)
        prev_date = datetime.datetime.now() - datetime.timedelta(days=1)

        expiration_date = date.strftime("%Y-%m-%d")
        self.api.set_expiration_date(expiration_date)
        self.assertEqual(self.api.expiration_date, expiration_date)

        expiration_date = "invalid"
        with self.assertRaises(MyPermobilClientException):
            self.api.set_expiration_date(expiration_date)

        expiration_date = prev_date.strftime("%Y-%m-%d")
        with self.assertRaises(MyPermobilClientException):
            self.api.set_expiration_date(expiration_date)

        expiration_date = ""
        with self.assertRaises(MyPermobilClientException):
            self.api.set_expiration_date(expiration_date)

    async def test_set_token(self):
        token = "a" * 256
        self.api.set_token(token)
        self.assertEqual(self.api.token, token)

        token = "invalid"
        with self.assertRaises(MyPermobilClientException):
            self.api.set_token(token)

        token = ""
        with self.assertRaises(MyPermobilClientException):
            self.api.set_token(token)

    async def test_set_code(self):
        code = "123456"
        self.api.set_code(code)
        self.assertEqual(self.api.code, code)

        code = "invalid"
        with self.assertRaises(MyPermobilClientException):
            self.api.set_code(code)

        code = "123456789"
        with self.assertRaises(MyPermobilClientException):
            self.api.set_code(code)

        code = ""
        with self.assertRaises(MyPermobilClientException):
            self.api.set_code(code)

        code = " "
        with self.assertRaises(MyPermobilClientException):
            self.api.set_code(code)

    async def test_set_region(self):
        region = "http://example.com"
        self.api.set_region(region)
        self.assertEqual(self.api.region, region)

        region = "not a valid region"
        with self.assertRaises(MyPermobilClientException):
            self.api.set_region(region)

        region = ""
        with self.assertRaises(MyPermobilClientException):
            self.api.set_region(region)

    async def test_set_product_id(self):
        id = "a" * 24
        self.api.set_product_id(id)
        self.assertEqual(self.api.product_id, id)

        region = "a" * 10
        with self.assertRaises(MyPermobilClientException):
            self.api.set_product_id(region)

        region = ""
        with self.assertRaises(MyPermobilClientException):
            self.api.set_product_id(region)

    async def test_auth_checks(self):
        # cannot authenticate without setting application name
        with self.assertRaises(MyPermobilClientException):
            self.api.self_authenticate()

        # cannot deauth without authenticating
        with self.assertRaises(MyPermobilClientException):
            self.api.deauthenticate()

        self.api.set_email("valid@email.com")
        self.api.set_region("http://example.com")
        self.api.set_code("123456")
        self.api.set_token("a" * 256)
        date = datetime.datetime.now() + datetime.timedelta(days=1)
        self.api.set_expiration_date(date.strftime("%Y-%m-%d"))
        self.api.set_application("test")
        self.api.self_authenticate()

        # cannot authenticate twice
        with self.assertRaises(MyPermobilClientException):
            self.api.self_authenticate()

    async def test_change_after_auth(self):
        self.api.set_email("valid@email.com")
        self.api.set_region("http://example.com")
        self.api.set_code("123456")
        self.api.set_token("a" * 256)
        date = datetime.datetime.now() + datetime.timedelta(days=1)
        self.api.set_expiration_date(date.strftime("%Y-%m-%d"))
        self.api.set_application("test")

        self.api.self_authenticate()
        assert self.api.headers == {"Authorization": f"Bearer {'a' * 256}"}

        with self.assertRaises(MyPermobilClientException):
            self.api.set_email("valid2@email.com")
        with self.assertRaises(MyPermobilClientException):
            self.api.set_region("http://new_region.com")
        with self.assertRaises(MyPermobilClientException):
            self.api.set_code("654321")
        with self.assertRaises(MyPermobilClientException):
            self.api.set_token("b" * 256)
        date = datetime.datetime.now() - datetime.timedelta(days=2)
        with self.assertRaises(MyPermobilClientException):
            self.api.set_expiration_date(date.strftime("%Y-%m-%d"))
        with self.assertRaises(MyPermobilClientException):
            self.api.set_application("new_application")


if __name__ == "__main__":
    unittest.main()
