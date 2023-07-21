"""Constants for the Permobil integration."""

GET = "get"
POST = "post"
PUT = "put"
DELETE = "delete"

EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"
MILES = "miles"
KILOMETERS = "kilometers"

GET_REGIONS = "https://cwcprod.permobil.com/api/v1/regions?includeFlags=on"
GET_REGIONS_NO_FLAGS = "https://cwcprod.permobil.com/api/v1/regions"

ENDPOINT_APPLICATIONLINKS = "/api/v1/users/applicationlinks"
ENDPOINT_APPLICATIONAUTHENTICATIONS = "/api/v1/users/applicationauthentications"

# Information endpoints
ENDPOINT_BATTERY_INFO = "/api/v1/products/battery-info"

BATTERY_STATE_OF_HEALTH = ["stateOfHealth"]
BATTERY_STATE_OF_CHARGE = ["stateOfCharge"]
BATTERY_CHARGING = ["charging"]
BATTERY_CHARGE_TIME_LEFT = ["chargeTimeLeft"]
BATTERY_DISTANCE_LEFT = ["distanceLeft"]
BATTERY_LOCAL_DISTANCE_LEFT = ["localDistanceLeft"]
BATTERY_INDOOR_DRIVE_TIME = ["indoorDriveTime"]
BATTERY_MAX_INDOOR_DRIVE_TIME = ["maxIndoorDriveTime"]
BATTERY_DISTANCE_UNIT = ["distanceUnit"]
BATTERY_MAX_AMPERE_HOURS = ["maxAmpereHours"]
BATTERY_AMPERE_HOURS_LEFT = ["ampereHoursLeft"]
BATTERY_MAX_DISTANCE_LEFT = ["maxDistanceLeft"]
BATTERY_TIMESTAMP = ["localTimestamp"]
BATTERY_LOCAL_TIMESTAMP = ["localTimestamp"]


ENDPOINT_DAILY_USAGE = "/api/v1/products/voiceaccess/dailyusage"

USAGE_DISTANCE = ["distance"]
USAGE_DISTANCE_UNIT = ["distanceUnit"]
USAGE_ADJUSTMENTS = ["adjustments"]


# The same info is available in the battery info endpoint
ENDPOINT_VA_CHARGE_TIME = "/api/v1/products/voiceaccess/chargetime"

CHARGE_TIME_UNKNOWN = ["unknown"]
CHARGE_CHARGING_NOW = ["chargingNow"]
CHARGE_CHARGE_TIME_LEFT = ["chargeTimeLeft"]
CHARGE_CHARGE_TIME_LEFT_MINUTES = ["minutes"]
CHARGE_CHARGE_TIME_LEFT_HOURS = ["hours"]


ENDPOINT_VA_CHAIR_STATUS = "/api/v1/products/voiceaccess/chairstatus"

STATUS_STATUS = ["status"]


ENDPOINT_VA_USAGE_RECORDS = "/api/v1/products/voiceaccess/usagerecords"

RECORDS_DISTANCE = ["distanceRecord"]
RECORDS_DISTANCE_UNIT = ["distanceUnit"]
RECORDS_DISTANCE_DATE = ["distanceRecordDate"]
RECORDS_SEATING = ["seatingRecord"]
RECORDS_SEATING_DATE = ["seatingRecordDate"]


ENDPOINT_PRODUCTS = "/api/v1/products"

PRODUCTS_ID = [0, "_id"]
PRODUCTS_MODEL = [0, "Model"]


ENDPOINT_PRODUCT_BY_ID = "/api/v1/products/{product_id}"

PRODUCT_BY_ID_UPDATED_AT = ["updatedAt"]
PRODUCT_BY_ID_MOST_RECENT = ["mostRecent"]
PRODUCT_BY_ID_MOST_RECENT_ODOMETER_TOTAL = [*PRODUCT_BY_ID_MOST_RECENT, "odometerTotal"]
PRODUCT_BY_ID_MOST_RECENT_ODOMETER_TRIP = [*PRODUCT_BY_ID_MOST_RECENT, "odometerTrip"]


ENDPOINT_PRODUCTS_POSITIONS = "/api/v1/products/{product_id}/positions"

POSITIONS_CURRENT = ["currentPosition"]
POSITIONS_PREVIOUS = ["previousPositions"]


ITEM_LOOKUP = {
    ENDPOINT_BATTERY_INFO: [
        BATTERY_STATE_OF_HEALTH,
        BATTERY_STATE_OF_CHARGE,
        BATTERY_CHARGING,
        BATTERY_CHARGE_TIME_LEFT,
        BATTERY_DISTANCE_LEFT,
        BATTERY_LOCAL_DISTANCE_LEFT,
        BATTERY_INDOOR_DRIVE_TIME,
        BATTERY_MAX_INDOOR_DRIVE_TIME,
        BATTERY_DISTANCE_UNIT,
        BATTERY_MAX_AMPERE_HOURS,
        BATTERY_AMPERE_HOURS_LEFT,
        BATTERY_MAX_DISTANCE_LEFT,
        BATTERY_TIMESTAMP,
        BATTERY_LOCAL_TIMESTAMP,
    ],
    ENDPOINT_DAILY_USAGE: [
        USAGE_DISTANCE,
        USAGE_DISTANCE_UNIT,
        USAGE_ADJUSTMENTS,
    ],
    ENDPOINT_VA_CHARGE_TIME: [
        CHARGE_TIME_UNKNOWN,
        CHARGE_CHARGING_NOW,
        CHARGE_CHARGE_TIME_LEFT,
        CHARGE_CHARGE_TIME_LEFT_MINUTES,
        CHARGE_CHARGE_TIME_LEFT_HOURS,
    ],
    ENDPOINT_VA_CHAIR_STATUS: [
        STATUS_STATUS,
    ],
    ENDPOINT_VA_USAGE_RECORDS: [
        RECORDS_DISTANCE,
        RECORDS_DISTANCE_UNIT,
        RECORDS_DISTANCE_DATE,
        RECORDS_SEATING,
        RECORDS_SEATING_DATE,
    ],
    ENDPOINT_PRODUCTS_POSITIONS: [
        POSITIONS_CURRENT,
        POSITIONS_PREVIOUS,
    ],
    ENDPOINT_PRODUCTS: [
        PRODUCTS_ID,
        PRODUCTS_MODEL,
    ],
    ENDPOINT_PRODUCT_BY_ID: [
        PRODUCT_BY_ID_MOST_RECENT,
        PRODUCT_BY_ID_MOST_RECENT_ODOMETER_TOTAL,
        PRODUCT_BY_ID_MOST_RECENT_ODOMETER_TRIP,
        PRODUCT_BY_ID_UPDATED_AT,
    ],
}

# when multiple endpoints have the same item, the FIRST one in the list will be used
ENDPOINT_LOOKUP = {
    str(item): endpoint
    for endpoint, items in list(ITEM_LOOKUP.items())[::-1]
    for item in items
}
