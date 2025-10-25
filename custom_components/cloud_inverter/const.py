"""Constants for Cloud Inverter integration."""

DOMAIN = "cloud_inverter"
MANUFACTURER = "SenergyTec"

SCAN_INTERVAL = 60  # 60 seconds

# Inverter data fields
INVERTER_FIELDS = {
    "solar_power": {"key": "Pac", "unit": "W", "type": "power"},
    "solar_energy_today": {"key": "EToday", "unit": "kWh", "type": "energy"},
    "solar_energy_total": {"key": "ETotal", "unit": "kWh", "type": "energy"},
    "peak_power": {"key": "Peackpower", "unit": "W", "type": "power"},
    "inverter_temp": {"key": "Tntc", "unit": "°C", "type": "temperature"},
    "grid_voltage": {"key": "gridVac", "unit": "V", "type": "voltage"},
    "grid_current": {"key": "gridIac", "unit": "A", "type": "current"},
    "grid_frequency": {"key": "gridFac", "unit": "Hz", "type": "frequency"},
    "grid_power": {"key": "gridCurrpac", "unit": "W", "type": "power"},
    "grid_export_today": {"key": "ETDay", "unit": "kWh", "type": "energy"},
    "grid_import_today": {"key": "EFDay", "unit": "kWh", "type": "energy"},
    "grid_export_total": {"key": "ETTotal", "unit": "kWh", "type": "energy"},
    "grid_import_total": {"key": "EFTotal", "unit": "kWh", "type": "energy"},
    "home_load_power": {"key": "epsCurrpac", "unit": "W", "type": "power"},
    "home_load_energy_today": {"key": "EPSDay", "unit": "kWh", "type": "energy"},
    "home_load_energy_total": {"key": "EPSTotal", "unit": "kWh", "type": "energy"},
    "battery_soc": {"key": "SOC", "unit": "%", "type": "percentage"},
    "battery_voltage": {"key": "volt", "unit": "V", "type": "voltage"},
    "battery_current": {"key": "cur", "unit": "A", "type": "current"},
    "battery_charge_power": {"key": "toPbat", "unit": "W", "type": "power"},
    "battery_discharge_power": {"key": "fromPbat", "unit": "W", "type": "power"},
    "battery_charge_total": {"key": "Etotal_batChrg", "unit": "kWh", "type": "energy"},
    "battery_discharge_total": {"key": "Etotal_batDischrg", "unit": "kWh", "type": "energy"},
    "self_consumption_rate": {"key": "Dailyself_userate", "unit": "%", "type": "percentage"},
    "self_sufficiency_rate": {"key": "Dailyself_sufficiencyrate", "unit": "%", "type": "percentage"},
    "wifi_strength": {"key": "WifiStrength", "unit": "%", "type": "percentage"},
}

# MPPT data
MPPT_FIELDS = {
    "pdc": {"key": "Pdc", "unit": "kW", "type": "power"},
    "vdc": {"key": "Vdc", "unit": "V", "type": "voltage"},
    "idc": {"key": "Idc", "unit": "A", "type": "current"},
}
