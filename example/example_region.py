"""Example of how to authenticate a MyPermobil instance"""

import asyncio
import mypermobil


async def main():
    """Example of how to authenticate a MyPermobil instance"""

    # Create a session
    # mypermobil uses aiohttp.ClientSession for the requests
    session = await mypermobil.create_session()
    p_api = mypermobil.MyPermobil(
        session=session,
        application="example-application",
    )
    try:
        regions = await p_api.request_regions(include_internal=True)
        print("\n".join([regions[region_id].get("url") for region_id in regions]))
    finally:
        await p_api.close_session()


if __name__ == "__main__":
    asyncio.run(main())
