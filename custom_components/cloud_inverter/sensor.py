"""Sensor platform for Cloud Inverter integration."""
import logging
from typing import Any, Optional

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTemperature,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfFrequency,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INVERTER_FIELDS, MPPT_FIELDS, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for Cloud Inverter."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    inverter_id = data["inverter_id"]

    entities = []

    # Add main inverter sensors
    for sensor_name, field_info in INVERTER_FIELDS.items():
        entities.append(
            CloudInverterSensor(
                coordinator,
                inverter_id,
                sensor_name,
                field_info,
            )
        )

    # Add MPPT sensors (2 trackers max)
    for mppt_num in range(1, 3):
        for mppt_name, mppt_info in MPPT_FIELDS.items():
            entities.append(
                CloudInverterMPPTSensor(
                    coordinator,
                    inverter_id,
                    f"mppt{mppt_num}_{mppt_name}",
                    mppt_info,
                    mppt_num - 1,
                )
            )

    async_add_entities(entities)


class CloudInverterSensor(CoordinatorEntity, SensorEntity):
    """Cloud Inverter sensor entity."""

    def __init__(
        self,
        coordinator,
        inverter_id: str,
        sensor_name: str,
        field_info: dict,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.inverter_id = inverter_id
        self.sensor_name = sensor_name
        self.field_info = field_info
        self._attr_unique_id = f"{DOMAIN}_{inverter_id}_{sensor_name}"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        # Convert sensor_name to Title Case for display
        words = self.sensor_name.split("_")
        return " ".join(word.capitalize() for word in words)

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        try:
            if not self.coordinator.data:
                return None

            data = self.coordinator.data.get("data", {})
            field_key = self.field_info["key"]

            value = data.get(field_key)

            # Handle list values (take first element)
            if isinstance(value, list) and value:
                value = value[0]

            # Convert to appropriate type
            if value is not None:
                try:
                    float_value = float(value)
                    # Round to 2 decimals for most values
                    return round(float_value, 2)
                except (ValueError, TypeError):
                    return str(value) if value else None

            return None

        except Exception as e:
            _LOGGER.error(f"Error getting value for {self.sensor_name}: {e}")
            return None

    @property
    def native_unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement."""
        unit_map = {
            "W": UnitOfPower.WATT,
            "kW": UnitOfPower.KILO_WATT,
            "kWh": UnitOfEnergy.KILO_WATT_HOUR,
            "MWh": UnitOfEnergy.MEGA_WATT_HOUR,
            "°C": UnitOfTemperature.CELSIUS,
            "V": UnitOfElectricPotential.VOLT,
            "A": UnitOfElectricCurrent.AMPERE,
            "Hz": UnitOfFrequency.HERTZ,
            "%": PERCENTAGE,
            "Ah": "Ah",
        }
        unit = self.field_info.get("unit", "")
        return unit_map.get(unit, unit if unit else None)

    @property
    def device_class(self) -> Optional[str]:
        """Return the device class."""
        class_map = {
            "power": SensorDeviceClass.POWER,
            "energy": SensorDeviceClass.ENERGY,
            "temperature": SensorDeviceClass.TEMPERATURE,
            "voltage": SensorDeviceClass.VOLTAGE,
            "current": SensorDeviceClass.CURRENT,
            "frequency": SensorDeviceClass.FREQUENCY,
            "percentage": SensorDeviceClass.BATTERY,
            "battery": SensorDeviceClass.BATTERY,
        }
        return class_map.get(self.field_info.get("type", ""), None)

    @property
    def state_class(self) -> Optional[str]:
        """Return the state class."""
        sensor_type = self.field_info.get("type", "")
        
        if sensor_type == "energy":
            return SensorStateClass.TOTAL_INCREASING
        elif sensor_type == "power":
            return SensorStateClass.MEASUREMENT
        elif sensor_type in ("voltage", "current", "frequency", "temperature", "percentage"):
            return SensorStateClass.MEASUREMENT
        
        return None

    @property
    def device_info(self):
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self.inverter_id)},
            "manufacturer": MANUFACTURER,
            "name": f"Cloud Inverter {self.inverter_id}",
            "model": "SenergyTec Inverter",
            "via_device": (DOMAIN, "cloud_inverter_integration"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def should_poll(self) -> bool:
        """No polling needed, coordinator handles it."""
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        self.async_write_ha_state()


class CloudInverterMPPTSensor(CoordinatorEntity, SensorEntity):
    """Cloud Inverter MPPT sensor entity."""

    def __init__(
        self,
        coordinator,
        inverter_id: str,
        sensor_name: str,
        field_info: dict,
        mppt_index: int,
    ):
        """Initialize the MPPT sensor."""
        super().__init__(coordinator)
        self.inverter_id = inverter_id
        self.sensor_name = sensor_name
        self.field_info = field_info
        self.mppt_index = mppt_index
        self._attr_unique_id = f"{DOMAIN}_{inverter_id}_{sensor_name}"
        self._attr_has_entity_name = True

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        mppt_num = self.mppt_index + 1
        field_name = self.sensor_name.split("_")[1].upper()
        
        # Create readable name
        name_map = {
            "PDC": "Power",
            "VDC": "Voltage",
            "IDC": "Current",
        }
        
        field_display = name_map.get(field_name, field_name)
        return f"MPPT{mppt_num} {field_display}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        try:
            if not self.coordinator.data:
                return None

            data = self.coordinator.data.get("data", {})
            field_key = self.field_info["key"]

            value_list = data.get(field_key, [])

            if isinstance(value_list, list) and len(value_list) > self.mppt_index:
                value = value_list[self.mppt_index]
                try:
                    float_value = float(value)
                    return round(float_value, 3)
                except (ValueError, TypeError):
                    return None

            return None

        except Exception as e:
            _LOGGER.error(f"Error getting MPPT value: {e}")
            return None

    @property
    def native_unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement."""
        unit_map = {
            "kW": UnitOfPower.KILO_WATT,
            "V": UnitOfElectricPotential.VOLT,
            "A": UnitOfElectricCurrent.AMPERE,
        }
        unit = self.field_info.get("unit", "")
        return unit_map.get(unit, unit if unit else None)

    @property
    def device_class(self) -> Optional[str]:
        """Return the device class."""
        class_map = {
            "power": SensorDeviceClass.POWER,
            "voltage": SensorDeviceClass.VOLTAGE,
            "current": SensorDeviceClass.CURRENT,
        }
        return class_map.get(self.field_info.get("type", ""), None)

    @property
    def state_class(self) -> Optional[str]:
        """Return the state class."""
        return SensorStateClass.MEASUREMENT

    @property
    def device_info(self):
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self.inverter_id)},
            "manufacturer": MANUFACTURER,
            "name": f"Cloud Inverter {self.inverter_id}",
            "model": "SenergyTec Inverter",
            "via_device": (DOMAIN, "cloud_inverter_integration"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def should_poll(self) -> bool:
        """No polling needed, coordinator handles it."""
        return False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        self.async_write_ha_state()
