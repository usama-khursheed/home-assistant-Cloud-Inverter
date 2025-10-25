"""Constants for Cloud Inverter integration."""

DOMAIN = "cloud_inverter"
MANUFACTURER = "SenergyTec"

SCAN_INTERVAL = 60  # 60 seconds

# Inverter data fields mapping - Maps sensor name to API field
INVERTER_FIELDS = {
    # Solar Production
    "solar_pv_current_power": {"key": "Pac", "unit": "W", "type": "power"},
    "solar_production_today": {"key": "EToday", "unit": "kWh", "type": "energy"},
    "solar_production_all_time": {"key": "ETotal", "unit": "kWh", "type": "energy"},
    "peak_power_today": {"key": "Peackpower", "unit": "W", "type": "power"},
    
    # Battery Status
    "battery_soc": {"key": "SOC", "unit": "%", "type": "battery"},
    "battery_soh": {"key": "SOH", "unit": "%", "type": "battery"},
    "battery_voltage": {"key": "volt", "unit": "V", "type": "voltage"},
    "battery_ampere": {"key": "cur", "unit": "A", "type": "current"},
    "battery_charge_power": {"key": "toPbat", "unit": "W", "type": "power"},
    "battery_discharge_power": {"key": "fromPbat", "unit": "W", "type": "power"},
    "battery_type": {"key": "brand", "unit": "", "type": "text"},
    "battery_capacity": {"key": "capacity", "unit": "Ah", "type": "text"},
    "battery_charge_today": {"key": "batChrg", "unit": "kWh", "type": "energy"},
    "battery_charge_all_time": {"key": "Etotal_batChrg", "unit": "kWh", "type": "energy"},
    "battery_discharge_today": {"key": "batDischrg", "unit": "kWh", "type": "energy"},
    "battery_discharge_all_time": {"key": "Etotal_batDischrg", "unit": "kWh", "type": "energy"},
    
    # Grid Status
    "grid_voltage": {"key": "gridVac", "unit": "V", "type": "voltage"},
    "grid_ampere": {"key": "gridIac", "unit": "A", "type": "current"},
    "grid_frequency": {"key": "gridFac", "unit": "Hz", "type": "frequency"},
    "grid_export_today": {"key": "ETDay", "unit": "kWh", "type": "energy"},
    "grid_export_total": {"key": "ETTotal", "unit": "kWh", "type": "energy"},
    "grid_import_today": {"key": "EFDay", "unit": "kWh", "type": "energy"},
    "grid_import_total": {"key": "EFTotal", "unit": "kWh", "type": "energy"},
    
    # Home Load (EPS)
    "home_load_power": {"key": "epsCurrpac", "unit": "W", "type": "power"},
    "home_load_voltage": {"key": "epsVac", "unit": "V", "type": "voltage"},
    "home_load_ampere": {"key": "epsIac", "unit": "A", "type": "current"},
    "home_load_frequency": {"key": "epsFac", "unit": "Hz", "type": "frequency"},
    "home_load_today": {"key": "EPSDay", "unit": "kWh", "type": "energy"},
    "home_load_total": {"key": "EPSTotal", "unit": "kWh", "type": "energy"},
    
    # Heavy Load (Generator)
    "heavy_load_power": {"key": "genCurrpac", "unit": "W", "type": "power"},
    "heavy_load_voltage": {"key": "genVac", "unit": "V", "type": "voltage"},
    "heavy_load_ampere": {"key": "genIac", "unit": "A", "type": "current"},
    "heavy_load_frequency": {"key": "genFac", "unit": "Hz", "type": "frequency"},
    "heavy_load_today": {"key": "GENDay", "unit": "kWh", "type": "energy"},
    "heavy_load_total": {"key": "GENTotal", "unit": "kWh", "type": "energy"},
    
    # On-Grid Load (EV Charger)
    "on_grid_load_power": {"key": "loadCurrpac", "unit": "W", "type": "power"},
    "on_grid_load_voltage": {"key": "loadVac", "unit": "V", "type": "voltage"},
    "on_grid_load_ampere": {"key": "loadIac", "unit": "A", "type": "current"},
    "on_grid_load_frequency": {"key": "loadFac", "unit": "Hz", "type": "frequency"},
    "on_grid_load_today": {"key": "ELDay", "unit": "kWh", "type": "energy"},
    "on_grid_load_total": {"key": "ELTotal", "unit": "kWh", "type": "energy"},
    
    # System Information
    "inverter_temperature": {"key": "Tntc", "unit": "°C", "type": "temperature"},
    "inverter_model": {"key": "modelName", "unit": "", "type": "text"},
    "inverter_serial": {"key": "GoodsID", "unit": "", "type": "text"},
    "inverter_status": {"key": "ESP32Version", "unit": "", "type": "text"},
    "inverter_wifi_strength": {"key": "WifiStrength", "unit": "%", "type": "percentage"},
    "inverter_operating_mode": {"key": "Operatingmode", "unit": "", "type": "text"},
    "inverter_operating_status": {"key": "Operatingstatus", "unit": "", "type": "text"},
    "inverter_firmware_version": {"key": "FirmwareVersion", "unit": "", "type": "text"},
    "inverter_esp32_version": {"key": "ESP32Version", "unit": "", "type": "text"},
    
    # Efficiency Metrics
    "self_consumption_rate": {"key": "Dailyself_userate", "unit": "%", "type": "percentage"},
    "self_sufficiency_rate": {"key": "Dailyself_sufficiencyrate", "unit": "%", "type": "percentage"},
}

# MPPT Tracker data fields - Maps MPPT property to API field
MPPT_FIELDS = {
    "pdc": {"key": "Pdc", "unit": "kW", "type": "power"},
    "vdc": {"key": "Vdc", "unit": "V", "type": "voltage"},
    "idc": {"key": "Idc", "unit": "A", "type": "current"},
}

# Supported device models
SUPPORTED_MODELS = [
    "SM-ONYX-UL-6KW",
    "SM-ONYX-UL",
    "SolarMax",
]

# API Configuration
API_BASE_URL = "https://www.cloudinverter.net"
API_TIMEOUT = 30  # seconds
API_RETRIES = 3

# Home Assistant specific
HA_MIN_VERSION = "2024.11"

# Device configuration
DEVICE_MANUFACTURER = "SenergyTec"
DEVICE_MODEL = "Cloud Inverter"
DEVICE_NAME_PATTERN = "Cloud Inverter {}"

# State class types
STATE_CLASS_MEASUREMENT = "measurement"
STATE_CLASS_TOTAL_INCREASING = "total_increasing"

# Device class types
DEVICE_CLASS_POWER = "power"
DEVICE_CLASS_ENERGY = "energy"
DEVICE_CLASS_TEMPERATURE = "temperature"
DEVICE_CLASS_VOLTAGE = "voltage"
DEVICE_CLASS_CURRENT = "current"
DEVICE_CLASS_FREQUENCY = "frequency"
DEVICE_CLASS_BATTERY = "battery"
DEVICE_CLASS_SIGNAL_STRENGTH = "signal_strength"

# Unit of measurement mappings
UNIT_WATT = "W"
UNIT_KILOWATT = "kW"
UNIT_MEGAWATT = "MW"
UNIT_WATT_HOUR = "Wh"
UNIT_KILOWATT_HOUR = "kWh"
UNIT_MEGAWATT_HOUR = "MWh"
UNIT_VOLT = "V"
UNIT_AMPERE = "A"
UNIT_HERTZ = "Hz"
UNIT_CELSIUS = "°C"
UNIT_FAHRENHEIT = "°F"
UNIT_PERCENTAGE = "%"
UNIT_AH = "Ah"

# Operation modes
OPERATION_MODE_STANDBY = 0
OPERATION_MODE_CHARGING = 1
OPERATION_MODE_DISCHARGING = 2
OPERATION_MODE_ONLINE = 3

OPERATION_MODE_MAP = {
    "0": "Standby",
    "1": "Charging",
    "2": "Discharging",
    "3": "Online",
}

# Operating status codes
OPERATING_STATUS_MAP = {
    "0": "Initialization",
    "1": "Startup",
    "2": "Running",
    "3": "Idle",
    "4": "Error",
    "5": "Off-Grid",
}

# Battery types
BATTERY_TYPE_LITHIUM = "Lithium"
BATTERY_TYPE_LEAD_ACID = "Lead-Acid"
BATTERY_TYPE_LIFEPO4 = "LiFePO4"

# BMS Status codes
BMS_STATUS_MAP = {
    "0": "Normal",
    "1": "Warning",
    "2": "Error",
    "3": "Offline",
}

# Default configuration
DEFAULT_LANGUAGE = "en-US"
DEFAULT_TIMEZONE = "UTC"
DEFAULT_UPDATE_INTERVAL = SCAN_INTERVAL

# Conversion factors
KWH_TO_MWH = 1000
WH_TO_KWH = 1000

# Data validation
MIN_SOC = 0
MAX_SOC = 100
MIN_VOLTAGE = 0
MAX_VOLTAGE = 500
MIN_TEMP = -20
MAX_TEMP = 60

# Sensor configuration
SENSOR_PRECISION = 2
ENERGY_PRECISION = 2
POWER_PRECISION = 0
VOLTAGE_PRECISION = 1
CURRENT_PRECISION = 2
FREQUENCY_PRECISION = 2
TEMPERATURE_PRECISION = 1

# Error messages
ERROR_INVALID_CREDENTIALS = "Invalid username or password"
ERROR_CANNOT_CONNECT = "Cannot connect to Cloud Inverter servers"
ERROR_NO_INVERTERS = "No inverters found"
ERROR_NETWORK = "Network error"
ERROR_TIMEOUT = "Request timeout"
ERROR_UNKNOWN = "Unknown error"

# Success messages
SUCCESS_LOGIN = "Successfully logged in"
SUCCESS_DATA_FETCHED = "Data fetched successfully"

# Log levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"

# Polling intervals (in seconds)
POLL_INTERVAL_FAST = 30      # Real-time data
POLL_INTERVAL_NORMAL = 60    # Default
POLL_INTERVAL_SLOW = 300     # Less frequently changing data
POLL_INTERVAL_RARE = 3600    # Rarely changing data
