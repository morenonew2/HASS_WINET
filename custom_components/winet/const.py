"""Costanti per l'integrazione WINET."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "winet"

CONF_MODE = "mode"
MODE_LOCAL = "local"
MODE_CLOUD = "cloud"

CONF_API_KEY = "api_key"
CONF_MAX_POWER = "max_power"
DEFAULT_MAX_POWER = 4

SCAN_INTERVAL = timedelta(seconds=15)
REQUEST_TIMEOUT = 10

CLOUD_BASE_URL = "https://ws.cloudwinet.it/WiNetStove.svc/json"

MIN_AIR_TEMP = 10
MAX_AIR_TEMP = 40
MIN_WATER_TEMP = 40
MAX_WATER_TEMP = 80

# Stati normalizzati della stufa (uguali per API locale e cloud)
STATUS_OFF = "off"
STATUS_ON = "on"
STATUS_FLAME_WAIT = "flame_wait"
STATUS_STANDBY = "standby"
STATUS_FINAL_CLEANING = "final_cleaning"
STATUS_BRAZIER_CLEANING = "brazier_cleaning"
STATUS_ALARM = "alarm"
STATUS_UNMANAGED = "unmanaged"
STATUS_UNKNOWN = "unknown"

STATUS_OPTIONS = [
    STATUS_OFF,
    STATUS_ON,
    STATUS_FLAME_WAIT,
    STATUS_STANDBY,
    STATUS_FINAL_CLEANING,
    STATUS_BRAZIER_CLEANING,
    STATUS_ALARM,
    STATUS_UNMANAGED,
    STATUS_UNKNOWN,
]

# Stati in cui la stufa e' considerata "accesa" (switch/climate)
ACTIVE_STATUSES = {STATUS_ON, STATUS_FLAME_WAIT, STATUS_STANDBY}
