# MyPermobil-API

## Description

This is a subset of the MyPermobil API, originally published to be used with HomeAssistant.

## Installation

The package is available on [pypi.org](https://pypi.org/project/mypermobil/) and installed with the command

    python -m pip install mypermobil 

It can also be manually installed by

    git clone  https://github.com/IsakNyberg/mypermobil.git
    cd mypermobil
    python -m pip install .

# REST API

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
