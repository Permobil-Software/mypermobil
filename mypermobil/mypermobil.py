"""Permobil API."""

import asyncio
import datetime
import re

import aiohttp
from aiocache import Cache

from .const import (
    ENDPOINT_APPLICATIONAUTHENTICATIONS,
    ENDPOINT_APPLICATIONLINKS,
    ENDPOINT_LOOKUP,
    GET_REGIONS,
    EMAIL_REGEX,
)

# TODO replace asserts with exceptions


class MyPermobilAPIException(Exception):
    """Permobil API Exception. Exception raised when the API returns an error."""


class MyPermobilClientException(Exception):
    """Permobil API Exception. Exception raised when the Client is used incorrectly."""


CACHE: Cache = Cache()
CACHE_TTL = 5 * 60  # 5 minutes
CACHE_LOCKS = {}


def cacheable(func):
    """Decorator to cache function calls for methods that
    fetch multiple data points from the API.
    """

    async def wrapper(*args, **kwargs):
        """wrapper."""
        key = func.__name__ + str(args) + str(kwargs)
        cached_data = await CACHE.get(key)
        if cached_data:
            return cached_data

        if key in CACHE_LOCKS:
            await CACHE_LOCKS[key].wait()
            return await CACHE.get(key)

        CACHE_LOCKS[key] = asyncio.Event()

        try:
            response = await func(*args, **kwargs)
            await CACHE.set(key, response, ttl=CACHE_TTL)
        finally:
            CACHE_LOCKS[key].set()
            del CACHE_LOCKS[key]
        return response

    return wrapper


def validate_email(email: str) -> str:
    """Validates an email."""
    if not email:
        raise MyPermobilClientException("Missing email")
    if not re.match(EMAIL_REGEX, email):
        raise MyPermobilClientException("Invalid email")
    return email


def validate_code(code: str) -> str:
    """Validates an code."""
    try:
        _ = int(code)
    except ValueError as err:
        raise MyPermobilClientException("Code must be a number") from err
    if len(code) != 6:
        # the code must be 6 digits long
        raise MyPermobilClientException("Invalid code")
    return code


def validate_token(token: str) -> str:
    """Validates an token."""
    if not token or len(token) != 256:
        # the token must be 256 characters long
        raise MyPermobilClientException("Invalid token")
    return token


def validate_expiration_date(expiration_date: str) -> str:
    """Validates an expiration date, both format and value."""
    if not expiration_date:
        raise MyPermobilClientException("Missing expiration date")
    date = None
    try:
        date = datetime.datetime.strptime(expiration_date, "%Y-%m-%d")
    except ValueError as err:
        raise MyPermobilClientException("Invalid expiration date") from err
    # check if the expiration date is in the future
    if date < datetime.datetime.now():
        raise MyPermobilClientException("Expired token")
    return expiration_date


async def create_session():
    """Create a client session."""
    return aiohttp.ClientSession()


class MyPermobil:
    """Permobil API."""

    def __init__(
        self,
        application: str,
        session: aiohttp.ClientSession,
        email: str = None,
        region: str = None,
        code: int = None,
        token: str = None,
        expiration_date: str = None,
        request_timeout: int = 10,
    ) -> None:
        """Initialize."""
        self.application = application
        self.session = session
        self.email = email
        self.region = region
        self.code = code
        self.token = token
        self.expiration_date = expiration_date
        self.request_timeout = request_timeout

        self.authenticated = False

    # Magic methods
    def __str__(self) -> str:
        """str."""
        return f"MyPermobil({self.application}, {self.email}, {self.region}, {self.code}, {self.token}, {self.headers}, {self.expiration_date})"

    # Selectors
    @property
    def headers(self):
        """headers."""
        assert self.authenticated is True
        return {"Authorization": f"Bearer {self.token}"}

    def set_email(self, email: str):
        """Set email."""
        assert self.authenticated is False
        self.email = validate_email(email)

    def set_region(self, region: str):
        """Set region."""
        assert self.authenticated is False
        self.region = region

    def set_code(self, code: int):
        """Set code."""
        assert self.authenticated is False
        self.code = validate_code(code)

    def set_token(self, token: str):
        """Set token."""
        assert self.authenticated is False
        self.token = validate_token(token)

    def set_application(self, application: str):
        """Set application."""
        self.application = application

    async def close_session(self):
        """Close session."""
        await self.session.close()

    def self_authenticate(self):
        """authenticate. Manually set token and expiration date."""
        assert self.authenticated is False
        assert self.region is not None
        assert bool(self.application)
        validate_email(self.email)
        validate_token(self.token)
        validate_expiration_date(self.expiration_date)
        self.authenticated = True

    # API Methods
    @cacheable
    async def request_regions(
        self, include_icons: bool = False, include_internal: bool = False
    ):
        """Get regions."""
        response = await self.session.get(GET_REGIONS, timeout=10)
        if response.status == 200:
            response_json = await response.json()
            regions = {}
            for region in response_json:
                if not include_internal:
                    if (
                        region.get("backendPort") != 443
                        or region.get("serverType") != "Production"
                    ):
                        continue
                region_id = region.get("_id")
                regions[region_id] = {}
                regions[region_id]["name"] = region.get("name")
                regions[region_id]["port"] = region.get("backendPort")
                protocol = "https" if region.get("backendPort") == 443 else "http"
                regions[region_id]["url"] = f"{protocol}://{region.get('host')}"
                if include_icons:
                    regions[region_id]["icon"] = region.get("flag")
            return regions

        if response.status in (404, 500):
            text = await response.text()
            raise MyPermobilAPIException(text)

    async def request_region_names(self, include_internal: bool = False):
        """Get region names."""
        regions = await self.request_regions(
            include_icons=False, include_internal=include_internal
        )
        return {
            regions[region_id].get("name"): regions[region_id].get("url")
            for region_id in regions
        }

    async def request_application_code(
        self, email: str = None, region: str = None, application: str = None
    ):
        """Post application link."""
        assert self.authenticated is False
        if email is None:
            email = self.email
        if region is None:
            region = self.region
        if application is None:
            application = self.application

        assert email is not None
        assert region is not None
        assert application is not None

        email = validate_email(email)
        url = region + ENDPOINT_APPLICATIONLINKS
        response = await self.session.post(
            url,
            json={"username": email, "application": application},
            timeout=self.request_timeout,
        )
        if response.status != 204:
            text = await response.text()
            raise MyPermobilAPIException(text)
        return True

    async def request_application_token(
        self,
        email: str = None,
        code: int = None,
        application: str = None,
        expiration_date: str = None,
    ) -> str:
        """Post the application token."""
        assert self.authenticated is False

        if email is None:
            email = self.email
        if code is None:
            code = self.code
        if application is None:
            application = self.application

        email = validate_email(email)
        code = validate_code(code)
        url = self.region + ENDPOINT_APPLICATIONAUTHENTICATIONS
        response = await self.session.post(
            url,
            json={
                "username": email,
                "code": code,
                "application": application,
                "expirationDate": expiration_date,
            },
            timeout=self.request_timeout,
        )
        if response.status == 200:
            json = await response.json()
            self.set_token(json.get("token"))
            self.authenticated = True
            if expiration_date is None:
                # set expiration date to 1 year from now
                time_delta = datetime.timedelta(days=365)
                date = datetime.datetime.now() + time_delta
                expiration_date = date.strftime("%Y-%m-%d")
            self.expiration_date = expiration_date

        elif response.status in (400, 401, 403, 500):
            resp = await response.json()
            raise MyPermobilAPIException(resp.get("error", resp))
        else:
            text = await response.text()
            raise MyPermobilAPIException(text)

        return self.token, self.expiration_date

    async def request_item(
        self, item: str, headers: dict = None
    ) -> str | int | float | bool:
        """Takes and item, finds the endpoint and makes the request."""
        if headers is None:
            headers = self.headers
        assert headers is not None

        endpoint = ENDPOINT_LOOKUP.get(item)
        if endpoint is None:
            raise MyPermobilClientException(f"Invalid item: {item}")
        response = await self.request_endpoint(endpoint, headers)
        return response.get(item)

    @cacheable
    async def request_endpoint(self, endpoint: str, headers: dict = None) -> dict:
        """Makes a request to an endpoint."""
        if headers is None:
            headers = self.headers
        assert headers is not None

        resp = await self.session.get(
            self.region + endpoint,
            headers=headers,
            timeout=self.request_timeout,
        )
        if resp.status >= 200 and resp.status < 300:
            return await resp.json()
        else:
            text = await resp.text()
            status = resp.status
            raise MyPermobilAPIException(f"Permobil API {status}: {text}")
