# Home Assistant PCA9685 PWM custom integration

**This is a spin-off from an original Home Assistant integration which was removed in Home Assistant Core 2022.4. The original rpi_gpi_pwm was stored [here](https://github.com/RedMeKool/HA-Raspberry-pi-GPIO-PWM/) but due to changes in 2022.7.5 support for pca9685 PWM devices was dropped. This module brings back  support for the pca9685 PWM LED driver in a separate component.**

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

**Description.**

The pca9685 component allows to control multiple lights using pulse-width modulation, for example LED strips. It supports one-color, RGB and RGBW LEDs driven by pca9685 devices. A PWM output can also be configured as a number. Connection to the pca9685 devices is made via the I2C bus.

For more details about the pca9685 I2C PWM LED controller you can find the datasheets here:
- [PCA9685](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf)

**This integration can set up the following platforms.**

Platform | Description
-- | --
`light` | Write LED signal to digital PWM outputs.
`number` | Writes signal represented by a number to PWM outputs.




### HACS (Preferred)
1. [Add](http://homeassistant.local:8123/hacs/integrations) the custom integration repository: https://github.com/domectrl/ha-pca9685
2. Select `PCA9685` in the Integration tab and click `download`
3. Restart Home Assistant
4. Done!

### Manual
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `pca9685`.
1. Download _all_ the files from the `custom_components//` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant

## Configuration via user interface:
* Configuration via user interface is not yet supported

## YAML Configuration

This integration can be configured and set up manually via YAML. To enable the light or number in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

light:
  - platform: pca9685
    leds:
      - name: Lightstrip Cupboard
        unique_id: lightstrip_cupboard
        pins: 10

number:
  - platform: pca9685
    numbers:
      - name: Test number
        pin: 12
```

### Configuration parameters

***Generic settings:***
- name: Name of the LED.
  > required: true | type: string
- frequency: The PWM frequency. 
  > required: false | type: int
- address: I2C address of the LED driver
  > required: false | default: 0x40 | type: int

***Light specific settings:***
- leds: List of LEDs.
  > required: true | type: map
- pins: The pins connected to the LED as a list. For single LED, assign one integer, for RGB assign 3 integers, for RGBW assign 4. Numbering starts from 0 up to 15.
  > required: true | type: [int]
- unique_id: The unique ID of the light.
  > required: false | default: None | type: string
- multi: If the LED should switch multiple LED pins.
  > required: false | default: false | type: boolean

***number specific settings:***
- numbers: List of the numbers.
  > required: true | type: map
- pin: The pin connected to the number. Numbering starts from 0 up to 15.
  > required: true | type: int
- invert: Invert signal of the PWM generator (only available for the number platform)
  > required: false | default: false | type: boolean
- minimum: Minimal (clipping) value of the number.
  > required: false | default: 0 | type: float
- maximum: Maximal (clipping) value of the number. 
  > required: false| default: 100 | type: float
- normalize_lower: Lower value to normalize the output of the PWM signal on.
  > required: false | default: 0 | type: float
- normalize_upper: Upper value to normalize the output of the PWM output on.
  > required: false | default: 100 | type: float

### Full configuration example

```yaml
light:
  - platform: pca9685
    leds:
      - name: Lightstrip Simple
        unique_id: lightstrip_simple
        pins: 10
        address: 65
      - name: Lightstrip RGB
        unique_id: lightstrip_rgb
        pins: [2,5,9]
        address: 65
      - name: Lightstrip RGBW
        unique_id: lightstrip_rgbw
        pins: [1,2,4,6]
        address: 65
      - name: Lightstrip Multiple
        unique_id: lightstrip_multiple
        pins: [1,2,3]
        multi: true
        address: 65

number:
  - platform: pca9685
    numbers:
      - name: Test number
        pin: 12
        frequency: 1000
        invert: true
        minimum: 11.5
        maximum: 75.7
        normalize_lower: -10.8
        normalize_upper: 200.5
        address: 65

```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/domectrl/ha-pca9685.svg?style=for-the-badge
[commits]: https://github.com/domectrl/ha-pca9685/commits/main
[hacs]: https://hacs.xyz/
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/domectrl/ha-pca9685.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-domectrl-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/domectrl/ha-pca9685.svg?style=for-the-badge
[releases]: https://github.com/domectrl/ha-pca9685/releases
