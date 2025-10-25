"""Cloud Inverter integration for Home Assistant."""
import asyncio
import logging
from datetime import timedelta
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .api import CloudInverterAPI
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cloud Inverter from a config entry."""
    _LOGGER.debug("Setting up Cloud Inverter integration")
    
    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    inverter_id = entry.data.get("inverter_id")

    api = CloudInverterAPI(username=username, password=password)

    async def async_update_data():
        """Fetch data from Cloud Inverter API."""
        try:
            _LOGGER.debug("Fetching data from Cloud Inverter API")
            data = await api.get_all_data()
            
            if not data.get("success"):
                _LOGGER.error("Failed to fetch inverter data")
                raise UpdateFailed("Failed to fetch inverter data from Cloud Inverter API")
            
            return data
            
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout fetching data from Cloud Inverter")
            raise UpdateFailed(f"Timeout communicating with Cloud Inverter API: {err}") from err
            
        except Exception as err:
            _LOGGER.error(f"Error communicating with Cloud Inverter API: {err}")
            raise UpdateFailed(f"Error communicating with Cloud Inverter API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.info(f"Successfully connected to Cloud Inverter: {inverter_id}")
    except UpdateFailed as err:
        _LOGGER.error(f"Failed to load Cloud Inverter data: {err}")
        raise ConfigEntryNotReady(f"Failed to load Cloud Inverter data: {err}") from err
    except Exception as err:
        _LOGGER.error(f"Unexpected error during setup: {err}")
        raise ConfigEntryNotReady(f"Unexpected error during setup: {err}") from err

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "inverter_id": inverter_id,
    }

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Add listener for options flow
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    _LOGGER.debug(f"Cloud Inverter setup complete for {inverter_id}")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug(f"Unloading Cloud Inverter entry: {entry.entry_id}")
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Clean up API session and remove from hass.data
        if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            api = hass.data[DOMAIN][entry.entry_id].get("api")
            if api:
                _LOGGER.debug("Closing Cloud Inverter API session")
                await api.close()
            
            # Remove entry from hass.data
            hass.data[DOMAIN].pop(entry.entry_id)
            
            # Clean up DOMAIN if empty
            if not hass.data[DOMAIN]:
                hass.data.pop(DOMAIN)
    
    _LOGGER.info(f"Successfully unloaded Cloud Inverter entry: {entry.entry_id}")
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug(f"Options updated for Cloud Inverter entry: {entry.entry_id}")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    _LOGGER.info(f"Removing Cloud Inverter entry: {entry.entry_id}")
    
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        api = hass.data[DOMAIN][entry.entry_id].get("api")
        if api:
            await api.close()


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Cloud Inverter integration from YAML (if supported in future)."""
    _LOGGER.debug("Cloud Inverter async_setup called")
    # Currently only supports config flow, not YAML configuration
    return True
