"""Sensor platform for Cloud Inverter."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import CloudInverterAPI
from .const import (
    DOMAIN,
    UPDATE_INTERVAL,
    CONF_USERNAME,
    CONF_PASSWORD,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cloud Inverter sensors."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    
    api = CloudInverterAPI(username, password)
    
    # Create coordinator
    coordinator = CloudInverterDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    
    # Create all sensors
    sensors = []
    
    # Photovoltaic (Solar) Sensors
    sensors.extend([
        CloudInverterSensor(coordinator, "Pac", "PV Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "Vdc_0", "PV Voltage MPPT1", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "Vdc_1", "PV Voltage MPPT2", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "Idc_0", "PV Current MPPT1", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "Idc_1", "PV Current MPPT2", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "Pdc_0", "PV Power MPPT1", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "Pdc_1", "PV Power MPPT2", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    ])
    
    # Production Sensors
    sensors.extend([
        CloudInverterSensor(coordinator, "EToday", "Daily Energy", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "ETotal", "Total Energy", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "Peackpower", "Peak Power Today", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    ])
    
    # Grid Sensors
    sensors.extend([
        CloudInverterSensor(coordinator, "gridVac", "Grid Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "gridIac", "Grid Current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "gridFac", "Grid Frequency", UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "gridCurrpac", "Grid Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "ETDay", "Grid Export Today", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "EFDay", "Grid Import Today", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "ETTotal", "Grid Export Total", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "EFTotal", "Grid Import Total", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    ])
    
    # Battery Sensors
    sensors.extend([
        CloudInverterSensor(coordinator, "volt", "Battery Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "cur", "Battery Current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "battery_power", "Battery Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "SOC", "Battery SOC", PERCENTAGE, SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "SOH", "Battery SOH", PERCENTAGE, None, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "toPbat", "Battery Charging Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "fromPbat", "Battery Discharging Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "batChrg", "Battery Charge Today", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "batDischrg", "Battery Discharge Today", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "Etotal_batChrg", "Battery Charge Total", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "Etotal_batDischrg", "Battery Discharge Total", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "brand", "Battery Type", None, None, None),
        CloudInverterSensor(coordinator, "capacity", "Battery Capacity", "Ah", None, SensorStateClass.MEASUREMENT),
    ])
    
    # Home Load (EPS) Sensors
    sensors.extend([
        CloudInverterSensor(coordinator, "epsVac", "Home Load Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "epsIac", "Home Load Current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "epsFac", "Home Load Frequency", UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "epsCurrpac", "Home Load Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "EPSDay", "Home Load Energy Today", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "EPSTotal", "Home Load Energy Total", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    ])
    
    # Heavy Load (Generator) Sensors
    sensors.extend([
        CloudInverterSensor(coordinator, "genVac", "Heavy Load Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "genIac", "Heavy Load Current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "genFac", "Heavy Load Frequency", UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "genCurrpac", "Heavy Load Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "GENDay", "Heavy Load Energy Today", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "GENTotal", "Heavy Load Energy Total", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    ])
    
    # On-Grid Load Sensors
    sensors.extend([
        CloudInverterSensor(coordinator, "loadVac", "On-Grid Load Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "loadIac", "On-Grid Load Current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "loadFac", "On-Grid Load Frequency", UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "loadCurrpac", "On-Grid Load Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "ELDay", "On-Grid Load Energy Today", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        CloudInverterSensor(coordinator, "ELTotal", "On-Grid Load Energy Total", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    ])
    
    # System Sensors
    sensors.extend([
        CloudInverterSensor(coordinator, "Tntc", "Inverter Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "WifiStrength", "WiFi Strength", PERCENTAGE, None, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "ESP32Version_Status", "Inverter Status", None, None, None),
        CloudInverterSensor(coordinator, "Operatingmode", "Operating Mode", None, None, None),
        CloudInverterSensor(coordinator, "Dailyself_userate", "Self Consumption Rate", PERCENTAGE, None, SensorStateClass.MEASUREMENT),
        CloudInverterSensor(coordinator, "Dailyself_sufficiencyrate", "Self Sufficiency Rate", PERCENTAGE, None, SensorStateClass.MEASUREMENT),
    ])
    
    # Device Info Sensors
    sensors.extend([
        CloudInverterSensor(coordinator, "modelName", "Model", None, None, None),
        CloudInverterSensor(coordinator, "GoodsID", "Serial Number", None, None, None),
        CloudInverterSensor(coordinator, "FirmwareVersion", "Firmware Version", None, None, None),
    ])
    
    async_add_entities(sensors)


class CloudInverterDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Cloud Inverter data."""

    def __init__(self, hass: HomeAssistant, api: CloudInverterAPI) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            data = await self.api.get_inverter_data()
            if not data:
                raise UpdateFailed("Failed to fetch inverter data")
            
            # Flatten the data structure for easier access
            flattened_data = {}
            
            # Extract main data
            if "data" in data:
                raw_data = data["data"]
                # Handle arrays in data
                if "Pac" in raw_data and isinstance(raw_data["Pac"], list) and raw_data["Pac"]:
                    flattened_data["Pac"] = raw_data["Pac"][0]
                if "Pdc" in raw_data and isinstance(raw_data["Pdc"], list):
                    if len(raw_data["Pdc"]) > 0:
                        flattened_data["Pdc_0"] = raw_data["Pdc"][0]
                    if len(raw_data["Pdc"]) > 1:
                        flattened_data["Pdc_1"] = raw_data["Pdc"][1]
                if "Vdc" in raw_data and isinstance(raw_data["Vdc"], list):
                    if len(raw_data["Vdc"]) > 0:
                        flattened_data["Vdc_0"] = raw_data["Vdc"][0]
                    if len(raw_data["Vdc"]) > 1:
                        flattened_data["Vdc_1"] = raw_data["Vdc"][1]
                if "Idc" in raw_data and isinstance(raw_data["Idc"], list):
                    if len(raw_data["Idc"]) > 0:
                        flattened_data["Idc_0"] = raw_data["Idc"][0]
                    if len(raw_data["Idc"]) > 1:
                        flattened_data["Idc_1"] = raw_data["Idc"][1]
            
            # Copy all other data
            for key, value in data.items():
                if key != "data":
                    if isinstance(value, list) and value:
                        flattened_data[key] = value[0]
                    elif isinstance(value, dict):
                        # Handle nested dicts like ESP32Version
                        for subkey, subvalue in value.items():
                            flattened_data[f"{key}_{subkey}"] = subvalue
                    else:
                        flattened_data[key] = value
            
            # Calculate battery power (charging is positive, discharging is negative)
            if "toPbat" in flattened_data and "fromPbat" in flattened_data:
                to_bat = float(flattened_data.get("toPbat", 0))
                from_bat = float(flattened_data.get("fromPbat", 0))
                flattened_data["battery_power"] = to_bat - from_bat
            
            return flattened_data
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


class CloudInverterSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Cloud Inverter sensor."""

    def __init__(
        self,
        coordinator: CloudInverterDataUpdateCoordinator,
        data_key: str,
        name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = f"Cloud Inverter {name}"
        self._attr_unique_id = f"cloud_inverter_{data_key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        
        value = self.coordinator.data.get(self._data_key)
        
        # Handle None or empty string values
        if value is None or value == "" or value == "-":
            return None
        
        # Try to convert to float for numeric values
        try:
            return float(value)
        except (ValueError, TypeError):
            return value

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.data.get("GoodsID", "unknown"))},
            "name": f"Cloud Inverter {self.coordinator.data.get('modelName', 'Unknown')}",
            "manufacturer": "SolarMax",
            "model": self.coordinator.data.get("modelName", "Unknown"),
            "sw_version": self.coordinator.data.get("FirmwareVersion", "Unknown"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None
