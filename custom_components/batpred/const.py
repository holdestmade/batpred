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

# Config entry keys - Basic
CONF_PREFIX = "prefix"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_TIMEZONE = "timezone"
CONF_THREADS = "threads"

# Config entry keys - Currency & Rates
CONF_CURRENCY_SYMBOLS = "currency_symbols"
CONF_METRIC_OCTOPUS_IMPORT = "metric_octopus_import"
CONF_METRIC_OCTOPUS_EXPORT = "metric_octopus_export"
CONF_METRIC_STANDING_CHARGE = "metric_standing_charge"
CONF_OCTOPUS_SAVING_SESSION = "octopus_saving_session"
CONF_OCTOPUS_SAVING_SESSION_OCTOPOINTS_PER_PENNY = "octopus_saving_session_octopoints_per_penny"

# Config entry keys - Solar & Forecast
CONF_SOLCAST_API_KEY = "solcast_api_key"
CONF_SOLCAST_HOST = "solcast_host"
CONF_SOLCAST_POLL_HOURS = "solcast_poll_hours"

# Config entry keys - Inverter
CONF_INVERTER_TYPE = "inverter_type"
CONF_NUM_INVERTERS = "num_inverters"
CONF_INVERTER_LIMIT = "inverter_limit"
CONF_INVERTER_LIMIT_CHARGE = "inverter_limit_charge"
CONF_INVERTER_LIMIT_DISCHARGE = "inverter_limit_discharge"
CONF_INVERTER_RESERVE_MAX = "inverter_reserve_max"
CONF_BALANCE_INVERTERS_SECONDS = "balance_inverters_seconds"

# Config entry keys - Sensor entity mappings
CONF_GESERIAL = "geserial"
CONF_LOAD_TODAY = "load_today"
CONF_IMPORT_TODAY = "import_today"
CONF_EXPORT_TODAY = "export_today"
CONF_PV_TODAY = "pv_today"
CONF_BATTERY_POWER = "battery_power"
CONF_PV_POWER = "pv_power"
CONF_LOAD_POWER = "load_power"
CONF_GRID_POWER = "grid_power"
CONF_SOC_KW = "soc_kw"
CONF_SOC_MAX = "soc_max"
CONF_INVERTER_MODE = "inverter_mode"

# Config entry keys - Control entity mappings
CONF_CHARGE_RATE = "charge_rate"
CONF_DISCHARGE_RATE = "discharge_rate"
CONF_RESERVE = "reserve"
CONF_CHARGE_START_TIME = "charge_start_time"
CONF_CHARGE_END_TIME = "charge_end_time"
CONF_DISCHARGE_START_TIME = "discharge_start_time"
CONF_DISCHARGE_END_TIME = "discharge_end_time"

# Config entry keys - Advanced / other
CONF_LOAD_FILTER_THRESHOLD = "load_filter_threshold"
CONF_BATTERY_SCALING = "battery_scaling"
CONF_IMPORT_EXPORT_SCALING = "import_export_scaling"
CONF_DAYS_PREVIOUS = "days_previous"
CONF_FORECAST_HOURS = "forecast_hours"

# Default values
DEFAULT_TIMEZONE = "Europe/London"
DEFAULT_THREADS = "auto"
DEFAULT_CURRENCY_SYMBOLS = "£\np"
DEFAULT_SOLCAST_HOST = "https://api.solcast.com.au/"
DEFAULT_SOLCAST_POLL_HOURS = 8
DEFAULT_INVERTER_TYPE = "GE"
DEFAULT_NUM_INVERTERS = 1
DEFAULT_INVERTER_RESERVE_MAX = 98
DEFAULT_BALANCE_INVERTERS_SECONDS = 60
DEFAULT_LOAD_FILTER_THRESHOLD = 30
DEFAULT_BATTERY_SCALING = "1.0"
DEFAULT_IMPORT_EXPORT_SCALING = 1.0
DEFAULT_DAYS_PREVIOUS = "7"
DEFAULT_FORECAST_HOURS = 48
DEFAULT_OCTOPUS_SAVING_SESSION_OCTOPOINTS_PER_PENNY = 8

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
