"""Support for numbers that can be controlled using PWM."""
from __future__ import annotations

import logging
from typing import Any

from pwmled.driver.pca9685 import Pca9685Driver
import voluptuous as vol

from homeassistant.components.number import (
    DEFAULT_MAX_VALUE,
    DEFAULT_MIN_VALUE,
    DEFAULT_STEP,
    PLATFORM_SCHEMA,
    RestoreNumber,
)
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_MAXIMUM,
    CONF_MINIMUM,
    CONF_MODE,
    CONF_NAME,
)
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_FREQUENCY,
)

CONF_NUMBERS = "numbers"
CONF_PIN = "pin"
CONF_INVERT = "invert"
CONF_STEP = "step"

MODE_SLIDER = "slider"
MODE_BOX = "box"
MODE_AUTO = "auto"

ATTR_FREQUENCY = "frequency"
ATTR_INVERT = "invert"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NUMBERS): vol.All(
            cv.ensure_list,
            [
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_PIN): cv.positive_int,
                    vol.Optional(CONF_INVERT, default=False): cv.boolean,
                    vol.Optional(CONF_FREQUENCY): cv.positive_int,
                    vol.Optional(CONF_ADDRESS): cv.byte,
                    vol.Optional(CONF_MINIMUM, default=DEFAULT_MIN_VALUE): vol.Coerce(
                        float
                    ),
                    vol.Optional(CONF_MAXIMUM, default=DEFAULT_MAX_VALUE): vol.Coerce(
                        float
                    ),
                    vol.Optional(CONF_STEP, default=DEFAULT_STEP): cv.positive_float,
                    vol.Optional(CONF_MODE, default=MODE_SLIDER): vol.In(
                        [MODE_BOX, MODE_SLIDER, MODE_AUTO]
                    ),
                }
            ],
        )
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the PWM-output numbers."""
    numbers = []
    for number_conf in config[CONF_NUMBERS]:
        pin = number_conf[CONF_PIN]
        opt_args = {}
        if CONF_FREQUENCY in number_conf:
            opt_args["freq"] = number_conf[CONF_FREQUENCY]
        if CONF_ADDRESS in number_conf:
            opt_args["address"] = number_conf[CONF_ADDRESS]
        driver = Pca9685Driver([pin], **opt_args)
        number = PwmNumber(hass, number_conf, driver)
        numbers.append(number)

    add_entities(numbers)


class PwmNumber(RestoreNumber):
    """Representation of a simple  PWM output."""

    def __init__(self, hass, config, driver):
        """Initialize one-color PWM LED."""
        self._driver = driver
        self._config = config
        self._hass = hass
        self._attr_native_min_value = config[CONF_MINIMUM]
        self._attr_native_max_value = config[CONF_MAXIMUM]
        self._attr_native_step = config[CONF_STEP]
        self._attr_mode = config[CONF_MODE]
        self._attr_native_value = config[CONF_MINIMUM]

    async def async_added_to_hass(self):
        """Handle entity about to be added to hass event."""
        await super().async_added_to_hass()
        if last_data := await self.async_get_last_number_data():
            try:
                await self.async_set_native_value(float(last_data.native_value))
            except ValueError:
                _LOGGER.warning(
                    "Could not read value %s from last state data for %s!",
                    last_data.native_value,
                    self.name,
                )

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the number."""
        return self._config[CONF_NAME]

    @property
    def frequency(self):
        """Return PWM frequency."""
        return self._config[CONF_FREQUENCY]

    @property
    def invert(self):
        """Return if output is inverted."""
        return self._config[CONF_INVERT]

    @property
    def capability_attributes(self) -> dict[str, Any]:
        """Return capability attributes."""
        attr = super().capability_attributes
        attr[ATTR_FREQUENCY] = self.frequency
        attr[ATTR_INVERT] = self.invert
        return attr

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        # Clip value to limits (don't know if this is required?)
        if value < self._config[CONF_MINIMUM]:
            value = self._config[CONF_MINIMUM]
        if value > self._config[CONF_MAXIMUM]:
            value = self._config[CONF_MAXIMUM]

        # Scale range from 0..100 to 0..65535 (pca9685)
        max_pwm = 65535.0
        # In case the invert bit is on, invert the value
        used_value = value
        if self._config[CONF_INVERT]:
            used_value = 100.0 - value
        # Scale to range of the driver
        scaled_value = int(round((used_value / 100.0) * max_pwm))
        # Set value to driver
        self._driver._set_pwm([scaled_value])  # pylint: disable=W0212
        self._attr_native_value = value
        self.async_write_ha_state()