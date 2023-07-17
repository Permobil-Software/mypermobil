"""Test the region names request"""

import asyncio
import unittest
from unittest.mock import AsyncMock

from mypermobil import MyPermobil, create_session, MyPermobilAPIException


class TestRegion(unittest.TestCase):
    """Test the region names request"""

    def test_region(self):
        """Test the region names request"""

        async def region_name_test():
            """Test the region names request"""
            session = await create_session()
            api = MyPermobil("test", session)
            names = await api.request_region_names()
            await api.close_session()
            assert len(names) > 0

        async def region_with_flags():
            """Test the region with flags request"""
            session = await create_session()
            api = MyPermobil("test", session)
            regions = await api.request_regions(include_icons=True)
            await api.close_session()
            assert len(regions) > 0

        async def region_error():
            """Test the region error request"""
            session = AsyncMock()
            response = AsyncMock()
            response.status = 404
            response.text = AsyncMock(return_value="test")
            session.get = AsyncMock(return_value=response)
            api = MyPermobil("test", session)
            with self.assertRaises(MyPermobilAPIException):
                await api.request_regions(include_icons=True)

        asyncio.run(region_name_test())
        asyncio.run(region_with_flags())
        asyncio.run(region_error())


if __name__ == "__main__":
    unittest.main()
