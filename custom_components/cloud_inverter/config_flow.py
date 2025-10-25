"""Config flow for Cloud Inverter integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import CloudInverterAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_INVERTER_ID = "inverter_id"


class CloudInverterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cloud Inverter."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step - credentials entry."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                # Verify credentials
                api = CloudInverterAPI(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )

                if not await api.login():
                    errors["base"] = "invalid_auth"
                else:
                    # Login successful, store for next step
                    self.api = api
                    self.user_input = user_input
                    return await self.async_step_inverter_select()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception as e:
                _LOGGER.exception(f"Unexpected error: {e}")
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={},
        )

    async def async_step_inverter_select(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle inverter selection step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # User selected an inverter
            inverter_id = user_input[CONF_INVERTER_ID]
            return await self._create_entry(inverter_id)

        try:
            # Fetch available inverters
            inverters = await self.api.get_inverters()

            if not inverters:
                errors["base"] = "no_inverters"
                return self.async_abort(reason="no_inverters_found")

            # Create inverter selection dictionary
            inverter_dict = {
                inv.get("AutoID"): f"{inv.get('GoodsName', f'Inverter {inv.get(\"AutoID\")}')}"
                for inv in inverters
            }

            # If only one inverter, select it automatically
            if len(inverter_dict) == 1:
                inverter_id = list(inverter_dict.keys())[0]
                return await self._create_entry(inverter_id)

            # Show form for multiple inverters
            return self.async_show_form(
                step_id="inverter_select",
                data_schema=vol.Schema(
                    {vol.Required(CONF_INVERTER_ID): vol.In(inverter_dict)}
                ),
                errors=errors,
                description_placeholders={
                    "inverter_count": str(len(inverter_dict))
                },
            )

        except CannotConnect:
            errors["base"] = "cannot_connect"
        except Exception as e:
            _LOGGER.exception(f"Error fetching inverters: {e}")
            errors["base"] = "unknown"

        return self.async_abort(reason="error_fetching_inverters")

    async def _create_entry(self, inverter_id: str) -> FlowResult:
        """Create the config entry."""
        await self.async_set_unique_id(f"{DOMAIN}_{inverter_id}")
        self._abort_if_unique_id_configured()

        await self.api.close()

        return self.async_create_entry(
            title=f"Cloud Inverter - {inverter_id}",
            data={
                CONF_USERNAME: self.user_input[CONF_USERNAME],
                CONF_PASSWORD: self.user_input[CONF_PASSWORD],
                CONF_INVERTER_ID: inverter_id,
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid authentication."""
