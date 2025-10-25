"""Config flow for Cloud Inverter integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import CloudInverterAPI
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = CloudInverterAPI(data[CONF_USERNAME], data[CONF_PASSWORD])
    
    try:
        if not await api.test_connection():
            raise InvalidAuth
        
        # Get the list of inverters
        groups = await api.get_group_list()
        if not groups:
            raise NoInvertersFound
            
        return {"groups": groups, "api": api}
    except NoInvertersFound:
        await api.close()
        raise
    except Exception:
        await api.close()
        raise


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cloud Inverter."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.username = None
        self.password = None
        self.api = None
        self.inverters = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - username and password."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Store credentials and API
                self.username = user_input[CONF_USERNAME]
                self.password = user_input[CONF_PASSWORD]
                self.api = info["api"]
                
                # Get group details to show inverter options
                groups = info["groups"]
                inverter_options = {}
                
                for group in groups:
                    group_auto_id = str(group.get("AutoID"))
                    # Get detailed info for this group
                    detail = await self.api.get_group_detail(group_auto_id)
                    
                    if detail and "AllInverterList" in detail:
                        for inverter in detail["AllInverterList"]:
                            goods_id = inverter.get("GoodsID")
                            model_name = inverter.get("ModelName", "Unknown")
                            goods_name = inverter.get("GoodsName", goods_id)
                            
                            # Create a user-friendly display name
                            display_name = f"{model_name} - {goods_id}"
                            inverter_options[goods_id] = display_name
                            self.inverters.append({
                                "goods_id": goods_id,
                                "model": model_name,
                                "name": goods_name
                            })
                
                if not inverter_options:
                    raise NoInvertersFound
                
                # If only one inverter, skip selection and configure directly
                if len(inverter_options) == 1:
                    selected_goods_id = list(inverter_options.keys())[0]
                    return await self._create_entry(selected_goods_id)
                
                # Multiple inverters - show selection
                return await self.async_step_select_inverter(inverter_options)
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except NoInvertersFound:
                errors["base"] = "no_inverters"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            finally:
                # Clean up API if there was an error
                if errors and self.api:
                    await self.api.close()
                    self.api = None

        return self.async_show_form(
            step_id="user", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors,
            description_placeholders={
                "note": "Enter your CloudInverter.net login credentials"
            }
        )

    async def async_step_select_inverter(
        self, inverter_options: dict[str, str] = None, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle inverter selection step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            selected_goods_id = user_input["inverter"]
            return await self._create_entry(selected_goods_id)
        
        # Build the options dict if not provided
        if inverter_options is None:
            inverter_options = {}
            for inv in self.inverters:
                goods_id = inv["goods_id"]
                display_name = f"{inv['model']} - {goods_id}"
                inverter_options[goods_id] = display_name
        
        data_schema = vol.Schema(
            {
                vol.Required("inverter"): vol.In(inverter_options),
            }
        )
        
        return self.async_show_form(
            step_id="select_inverter",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "note": "Select your inverter. The ID shown matches the serial number on your inverter device."
            }
        )

    async def _create_entry(self, goods_id: str) -> FlowResult:
        """Create the config entry."""
        # Find the selected inverter info
        selected_inverter = None
        for inv in self.inverters:
            if inv["goods_id"] == goods_id:
                selected_inverter = inv
                break
        
        if not selected_inverter:
            selected_inverter = {"model": "Unknown", "name": goods_id}
        
        # Check if already configured
        await self.async_set_unique_id(f"{self.username}_{goods_id}")
        self._abort_if_unique_id_configured()
        
        # Clean up API
        if self.api:
            await self.api.close()
        
        title = f"Cloud Inverter ({selected_inverter['model']})"
        
        return self.async_create_entry(
            title=title,
            data={
                CONF_USERNAME: self.username,
                CONF_PASSWORD: self.password,
                "goods_id": goods_id,
                "model": selected_inverter["model"],
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class NoInvertersFound(HomeAssistantError):
    """Error to indicate no inverters were found."""
