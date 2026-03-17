"""Constants for the Batpred integration."""

DOMAIN = "batpred"
DEFAULT_NAME = "Batpred"
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

# Device names
DEVICE_INVERTER = "Inverter"
DEVICE_BATTERY = "Battery"
DEVICE_GRID = "Grid"
DEVICE_SOLAR = "Solar"
DEVICE_PREDICTION = "Prediction"
DEVICE_RATES = "Rates"
DEVICE_CAR = "Car Charging"

# Config entry keys
CONF_PREFIX = "prefix"
CONF_SCAN_INTERVAL = "scan_interval"

# Platform names
PLATFORMS = ["sensor", "binary_sensor", "select", "number", "switch"]

# Manufacturer info
MANUFACTURER = "Predbat"
MODEL = "Battery Prediction System"

# Services
SERVICE_FORCE_CHARGE = "force_charge"
SERVICE_FORCE_DISCHARGE = "force_discharge"
SERVICE_RESET_PLAN = "reset_plan"
SERVICE_REFRESH_RATES = "refresh_rates"

# Operating mode options (matching existing predbat PREDBAT_MODE_OPTIONS exactly)
PREDBAT_MODE_OPTIONS = ["Monitor", "Control SOC only", "Control charge", "Control charge & discharge"]

# Charge/discharge rate limits
CHARGE_RATE_MIN = 0
CHARGE_RATE_MAX = 10000
DISCHARGE_RATE_MIN = 0
DISCHARGE_RATE_MAX = 10000
