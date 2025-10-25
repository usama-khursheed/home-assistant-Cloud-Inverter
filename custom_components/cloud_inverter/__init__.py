"""The Cloud Inverter integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_GOODS_ID

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cloud Inverter from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Store the full config entry data
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
        "goods_id": entry.data.get(CONF_GOODS_ID),
    }
    
    _LOGGER.info(
        "Setting up Cloud Inverter integration for inverter: %s (Model: %s)",
        entry.data.get(CONF_GOODS_ID, "Unknown"),
        entry.data.get("model", "Unknown"),
    )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Unloaded Cloud Inverter integration for inverter: %s", 
                    entry.data.get(CONF_GOODS_ID, "Unknown"))
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
