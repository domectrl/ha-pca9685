"""The pca9685 PWM component."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_ADDR, CONF_BUS, CONF_FREQUENCY, DOMAIN, PCA9685_DRIVERS
from .pca_driver import PCA9685Driver

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.LIGHT, Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PCA9685 from a config entry."""
    # Create PCA driver for this platform
    pca_driver = PCA9685Driver(
        address=int(entry.data[CONF_ADDR]), i2c_bus=entry.data[CONF_BUS]
    )
    await pca_driver.set_pwm_frequency(entry.data[CONF_FREQUENCY])

    pca9685_data = hass.data.setdefault(DOMAIN, {})
    if PCA9685_DRIVERS not in pca9685_data:
        pca9685_data[PCA9685_DRIVERS] = {}
    # TODO@domectrl: check bus & address used in another driver?  # noqa: FIX002, TD003
    pca9685_data[PCA9685_DRIVERS][entry.entry_id] = pca_driver

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))
    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
