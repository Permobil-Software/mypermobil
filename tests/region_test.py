"""Test the region names request"""

import asyncio
import unittest

from mypermobil import MyPermobil, create_session


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

        asyncio.run(region_name_test())


if __name__ == "__main__":
    unittest.main()
