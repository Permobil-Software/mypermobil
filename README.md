# MyPermobil-API

[![PyPI version](https://badge.fury.io/py/mypermobil.svg)](https://badge.fury.io/py/mypermobil)

This is a subset of the MyPermobil API, originally published to be used with HomeAssistant.

## Installation

The package is available on [pypi.org](https://pypi.org/project/mypermobil/) and installed with the command

    python -m pip install mypermobil 

It can also be manually installed by

    git clone  https://github.com/IsakNyberg/mypermobil.git
    cd mypermobil
    python -m pip install .

## REST API

This API is a REST API that uses JSON as the data format. For most requests, the API requires an authentication token. The token is sent in the header of the request. The token can be created with the code in the example folder.

## Endpoints

Supported endpoints are listed in the const.py, custom endpoints are also possible as arguments to the get and post methods.
The available endpoints are:

    GET regions
    POST applicationlinks
    POST applicationauthentications
    GET battery-info
    GET voiceaccess/dailyusage
    GET voiceaccess/chargetime
    GET voiceaccess/chairstatus
    GET voiceaccess/usagerecords
    GET /api/v1/products
    GET /api/v1/products/{product_id}
    GET /api/v1/products/{product_id}/positions

Some endpoints require a product id, this can be found in the `PRODUCTS_ID` item from the by using the `GET ENDPOINT_PRODUCTS` endpoint. This value can be set in the `MyPermobil` class.

## MyPermobil Class

The `MyPermobil` class is the main class of the API. The class can store information needed for the requests and can be used to make requests to the API.
The MyPermobil class uses `aiohttp` to make requests are they can be made asynchronously. The `create_session` function can be used to create a session without the need to import `aiohttp`. Just remember to close the session when it is no longer needed.

The minimum example of the class can be instantiated with:

    session = create_session()
    p = MyPermobil("application_name", session)
    ...
    p.close_session()

To authenticate the app use the `request_application_code()` and `request_application_token()` methods. A detailed example can be found in the example folder.

If the app has already been authenticated, the class can be created with the data directly instead. The data will be locally validated with the `self_authenticate()` method.

        p = MyPermobil(
            application,
            session,
            email,
            region,
            code,
            token,
            expiration_date,
            product_id,
        )
        p.self_authenticate()

`application`, `session`, `email`, `region`, `token` and `expiration_date` are required to authenticate the app. The `product_id` is optional and can be set later.

## Items

Items are lists that describe the path needed to traverse the JSON tree of the corresponding endpoint that is associated with the item.
Each association is listed in the `ITEM_LOOKUP` with the reverse lookup in `ENDPOINT_LOOKUP` (however since items are not always unique, the `ENDPOINT_LOOKUP` will only return the first endpoint associated with the item).

An example is:

    PRODUCT_BY_ID_MOST_RECENT_ODOMETER_TOTAL = ["mostRecent", "odometerTotal"]
    ENDPOINT_PRODUCT_BY_ID = "/api/v1/products/{product_id}"

    {
        "_id": "649adb...e377",
        "WCSerial": "48...28",
        "BrandId": "567...f50c",
        "lastUpdated": "2023",
        "mostRecent": {
            "odometerTotal": 386944,     <-----
            "odometerTrip": 375795,
        },
        "battery": {...},
        "serviceAgreements": [...],
        "certificates": [...]
    }

In this scenario the `PRODUCT_BY_ID_MOST_RECENT_ODOMETER_TOTAL` item would return the value `386944` from the JSON tree.

### Adding new items

Adding a new item can be done in the const.py file. The item should be added next to its endpoint and then in the the `ITEM_LOOKUP` dictionary. The item should be a list of strings or number with each step needed to take in the JSON tree. If the  named with the following format:

    ENDPOINT_ENDPOINT_NAME = "/api/v1/endpointname"
    ENDPOINTNAME_ITEM_NEW = ["path", "to", "item", 0]

The item can then be added to the `ENDPOINT_LOOKUP` dictionary with the following format:

    ITEM_LOOKUP = {
        ...
        ENDPOINT_ENDPOINT_NAME: [
            ENDPOINTNAME_ITEM_1,
            ENDPOINTNAME_ITEM_2,
            ENDPOINTNAME_ITEM_NEW,   <-----
            ENDPOINTNAME_ITEM_3,
        ],
        ...
    }

Doing this will automatically add the item to the `ENDPOINT_LOOKUP` dictionary, if the item is unique.

The new item can then be accessed by using the `request_item` method in the `MyPermobil` class.

    MyPermobil.request_item(ENDPOINTNAME_ITEM_NEW)

Or if the item is not unique and the endpoint needs to be specified:

    MyPermobil.request_item(ENDPOINTNAME_ITEM_NEW, endpoint=ENDPOINT_ENDPOINT_NAME)

### Async

All requests are made asynchronously. This means that the requests can be made in parallel. For every methods that uses the `async` keyword it must be awaited. This can be done by using the `asyncio` library. This was done in order to comply with Home Assistant.

    import asyncio

    async def main():
        await p.request_regions()

    asyncio.run(main())

### Caching

Many of the requests have the `@cachable` decorator. This decorator will cache the response of the request for 5 minutes. This is to prevent the API from being overloaded with requests, in particular when multiple items to the same endpoint is requested.
