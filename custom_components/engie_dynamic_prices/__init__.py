"""Engie Dynamic Prices integration for Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change

from .coordinator import EngieCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Engie Dynamic Prices from a config entry."""
    session = async_get_clientsession(hass)
    coordinator = EngieCoordinator(hass, session)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Trigger a coordinator refresh at the top of every hour so that
    # current_price and next_price sensors update exactly when the hour rolls
    # over, regardless of when the integration was first loaded.
    async def _refresh_on_hour_change(now) -> None:
        await coordinator.async_refresh()

    entry.async_on_unload(
        async_track_time_change(hass, _refresh_on_hour_change, minute=0, second=0)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
