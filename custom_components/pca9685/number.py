"""Support for numbers that can be controlled using PWM."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import homeassistant.helpers.config_validation as cv
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
    CONF_PIN,
)
from pwmled.driver.pca9685 import Pca9685Driver

from .const import (
    ATTR_FREQUENCY,
    ATTR_INVERT,
    CONF_FREQUENCY,
    CONF_INVERT,
    CONF_NORMALIZE_LOWER,
    CONF_NORMALIZE_UPPER,
    CONF_NUMBERS,
    CONF_STEP,
    MODE_AUTO,
    MODE_BOX,
    MODE_SLIDER,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

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
                    vol.Optional(
                        CONF_NORMALIZE_LOWER, default=DEFAULT_MIN_VALUE
                    ): vol.Coerce(float),
                    vol.Optional(
                        CONF_NORMALIZE_UPPER, default=DEFAULT_MAX_VALUE
                    ): vol.Coerce(float),
                    vol.Optional(CONF_STEP, default=DEFAULT_STEP): cv.positive_float,
                    vol.Optional(CONF_MODE, default=MODE_SLIDER): vol.In(
                        [MODE_BOX, MODE_SLIDER, MODE_AUTO]
                    ),
                }
            ],
        )
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,  # noqa: ARG001
) -> None:
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

    def __init__(
        self, hass: HomeAssistant, config: ConfigType, driver: Pca9685Driver
    ) -> None:
        """Initialize one-color PWM LED."""
        self._driver = driver
        self._config = config
        self._hass = hass
        self._attr_native_min_value = config[CONF_MINIMUM]
        self._attr_native_max_value = config[CONF_MAXIMUM]
        self._attr_native_step = config[CONF_STEP]
        self._attr_mode = config[CONF_MODE]
        self._attr_native_value = config[CONF_MINIMUM]

    async def async_added_to_hass(self) -> None:
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
        else:
            await self.async_set_native_value(self._config[CONF_MINIMUM])

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def name(self) -> str:
        """Return the name of the number."""
        return self._config[CONF_NAME]

    @property
    def frequency(self) -> int:
        """Return PWM frequency."""
        return self._config[CONF_FREQUENCY]

    @property
    def invert(self) -> bool:
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
        value = max(value, self._config[CONF_MINIMUM])
        value = min(value, self._config[CONF_MAXIMUM])

        # In case the invert bit is on, invert the value
        used_value = value
        if self._config[CONF_INVERT]:
            used_value = self._config[CONF_NORMALIZE_UPPER] - value

        # Scale range from N_L..N_U to 0..65535 (pca9685)
        range_pwm = 65535.0
        range_value = (
            self._config[CONF_NORMALIZE_UPPER] - self._config[CONF_NORMALIZE_LOWER]
        )
        # Scale to range of the driver
        scaled_value = int(round((used_value / range_value) * range_pwm))
        # Set value to driver
        self._driver._set_pwm([scaled_value])  # noqa: SLF001
        self._attr_native_value = value
        self.schedule_update_ha_state()
