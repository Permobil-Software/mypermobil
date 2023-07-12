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

    # get email
    email = input("Email: ")
    p_api.set_email(email)
    is_internal = email.endswith("@permobil.com")
    # request regions
    region_names = await p_api.request_region_names(include_internal=is_internal)
    print("Regions:")
    print(", ".join([region for region in region_names]))
    region_name = input("Select one: ")
    while region_name not in region_names:
        region_name = input("Select one: ")
    region = region_names[region_name]
    p_api.set_region(region)

    # send code request
    await p_api.request_application_code()
    print("Check your email for a code")
    code = input("Code: ")
    while True:
        try:
            p_api.set_code(code)
            break
        except mypermobil.MyPermobilClientException as err:
            print(err)
            code = input("Code: ")

    # get token
    try:
        token, ttl = await p_api.request_application_token()
        # íf your instance is linked to a single account set the values
        p_api.set_token(token)
        p_api.set_expiration_date(ttl)
        print("Token:", token)
        print("Expiration:", ttl)
    except mypermobil.MyPermobilException as err:
        print(err)

    # mark as authenticated
    p_api.self_authenticate()

    #################
    #               #
    # Do stuff here #
    #               #
    #################

    # close session

    await p_api.close_session()


if __name__ == "__main__":
    asyncio.run(main())
