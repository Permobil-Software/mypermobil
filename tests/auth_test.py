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

    async def test_not_authenticated(self):
        with self.assertRaises(MyPermobilClientException):
            _ = self.api.headers
        assert not self.api.authenticated

    async def test_request_application_code(self):
        self.api.set_email("valid@email.com")
        self.api.set_region("http://example.com")
        resp = MagicMock(status=204)
        resp.text = AsyncMock(return_value="OK")
        self.api.make_request = AsyncMock(return_value=resp)
        await self.api.request_application_code()

    async def test_request_application_code_invalid_response(self):
        resp = MagicMock(status=400)
        resp.text = AsyncMock(return_value="Error")
        self.api.make_request = AsyncMock(return_value=resp)
        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_application_code(
                email="test@example.com",
                region="http://example.com",
                application="myapp",
            )

    async def test_request_application_code_client_errors(self):
        resp = MagicMock(status=400)
        resp.text = AsyncMock(return_value="Error")

        self.api.authenticated = True
        with self.assertRaises(MyPermobilClientException):
            await self.api.request_application_code(
                email="test@example.com",
                region="http://example.com",
            )

        self.api.authenticated = False
        self.api.application = ""
        with self.assertRaises(MyPermobilClientException):
            await self.api.request_application_code(
                email="test@example.com",
                region="http://example.com",
                application="",
            )

    async def test_request_application_token(self):
        resp = AsyncMock(status=200)
        resp.json = AsyncMock(return_value={"token": "mytoken"})
        self.api.make_request = AsyncMock(return_value=resp)
        self.api.set_email("test@example.com")
        self.api.set_code("123123")
        result = await self.api.request_application_token()
        expected_date = datetime.datetime.now() + datetime.timedelta(days=365)
        self.assertEqual(result, ("mytoken", expected_date.strftime("%Y-%m-%d")))

        # test that it cannot be done twice
        self.api.authenticated = True
        with self.assertRaises(MyPermobilClientException):
            await self.api.request_application_token()

    async def test_request_application_token_invalid_response(self):
        self.api.make_request = AsyncMock(return_value=MagicMock(status=401))
        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_application_token(
                email="test@example.com", code="123123"
            )

        self.api.make_request = AsyncMock(return_value=MagicMock(status=403))
        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_application_token(
                email="test@example.com", code="123123"
            )
        resp = AsyncMock(status=400)
        resp.json = AsyncMock(return_value={"error": "test"})
        self.api.make_request = AsyncMock(return_value=resp)
        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_application_token(
                email="test@example.com", code="123123"
            )

        resp = AsyncMock(status=123123)
        resp.test = AsyncMock(return_value="test")
        self.api.make_request = AsyncMock(return_value=resp)
        with self.assertRaises(MyPermobilAPIException):
            await self.api.request_application_token(
                email="test@example.com", code="123123"
            )

    async def test_reauthenticate(self):
        self.api.authenticated = True
        with self.assertRaises(MyPermobilClientException):
            self.api.self_reauthenticate()

        self.api.authenticated = False
        self.api.application = ""
        with self.assertRaises(MyPermobilClientException):
            self.api.self_reauthenticate()

        self.api.authenticated = False
        self.api.application = "test"
        self.api.self_reauthenticate()
        assert self.api.authenticated is False
        assert self.api.token == None
        assert self.api.expiration_date == None
        assert self.api.code == None

    async def test_deauthenticate(self):
        # test deauth when not authenticated
        self.api.authenticated = False
        self.api.set_email("test@example.com")
        self.api.set_code("123123")
        with self.assertRaises(MyPermobilClientException) as e:
            await self.api.deauthenticate()
            assert str(e.exception) == "Not authenticated"

        # test deauth when not application
        self.api.authenticated = True
        self.api.application = ""
        with self.assertRaises(MyPermobilClientException) as e:
            await self.api.deauthenticate()
            assert str(e.exception) == "Missing application name"

        self.api.authenticated = True
        self.api.application = "test"
        # test successful deauth
        text = AsyncMock(return_value="text")
        session = AsyncMock()
        session.make_request = AsyncMock(return_value=AsyncMock(status=123, text=text))
        self.api.session = session
        with self.assertRaises(MyPermobilAPIException):
            await self.api.deauthenticate()


if __name__ == "__main__":
    unittest.main()
