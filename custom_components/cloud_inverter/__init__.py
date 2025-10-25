"""Cloud Inverter integration for Home Assistant."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CloudInverterAPI
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cloud Inverter from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    inverter_id = entry.data.get("inverter_id")

    api = CloudInverterAPI(username=username, password=password)

    async def async_update_data():
        """Fetch data from Cloud Inverter API."""
        try:
            data = await api.get_all_data()
            if not data.get("success"):
                raise UpdateFailed("Failed to fetch inverter data")
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        _LOGGER.error(f"Failed to load Cloud Inverter data: {err}")
        return False

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "inverter_id": inverter_id,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Clean up API session
        if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            api = hass.data[DOMAIN][entry.entry_id].get("api")
            if api:
                await api.close()
            hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
