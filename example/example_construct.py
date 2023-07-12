"""Example of how to construct a MyPermobil instance"""

import asyncio
from datetime import datetime, timedelta
import mypermobil


async def main():
    """Example of how to construct a MyPermobil instance"""

    # Create a session
    # mypermobil uses aiohttp.ClientSession for the requests
    session = await mypermobil.create_session()
    email = "example@email.com"
    token = "a" * 256
    expiration = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    region = "https://region.com/api/v1"
    application = "example-application"
    p_api = mypermobil.MyPermobil(
        application=application,
        session=session,
        email=email,
        token=token,
        expiration_date=expiration,
        region=region,
    )
    # mark as authenticated
    p_api.self_authenticate()

    #################
    #               #
    # Do stuff here #
    #               #
    #################
    # p_api.request_item(mypermobil.BATTERY_STATE_OF_CHARGE)

    # close session

    await p_api.close_session()


if __name__ == "__main__":
    asyncio.run(main())
