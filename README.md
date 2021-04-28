<h2 align="center">Home Assistant Integration with Prana Recuperators</h2>

Home Assistant integration with Prana Recuperators. It utilizes [prana_rc](https://github.com/corvis/prana_rc) underneath which could be installed either on the same machine with Home Assistant or at some other location closer to Prana device. 

## Features

- No need to keep Home Assistant close to the Prana device. 
- Apart from the simple ON\OF speed control allows managing extra features like:
  - Heating mode
  - Winter mode
  - Brightness (read-only at the moment)
- Allows controlling input and output flows independently
- Automatic discovery of the prana devices

## How does it work

The configuration is done via Config Flow. You have to establish a connection with running [prana_rc](https://github.com/corvis/prana_rc) instance and then use Options dialog to connect to the particular device (auto-discovery is available as well as an ability to type in the mac address of the device).

Once the device is configured the integration will register a bunch of entities:

- Your __main FAN entity__ which represents prana recuperator. This is what you most likely will be using regularly. It allows turning on and off the device in locked flows mode and set a particular speed. It also publishes a bunch of attributes that represent the current device state e.g. display brightness, heater status, winter mode, etc.
- The light entity which represents __display brightness__. So far it is read-only so you won't be able to adjust brightens.
- Switches for __heating__ and __winter__ modes. Allows controlling heating and winter modes correspondingly.
- Fan entities for __input__ and __output__ flows could be used to put Prana into unlocked flows mode and control flows independently.

## Installation

1. Download release from the [releases section](https://github.com/corvis/homeassistant_prana/releases).
2. Unpack the archive and put the content of the `custom_components` directory under `custom_components` directory of your home assistant installation. 
3. Restart home assistant
4. Install Prana RC and run it in http server mode:
  - The easiest way with docker would be to use docker: ` CODE SAMPLE TBD `
  - Also consult with Prana RC [installation instructions](https://github.com/corvis/prana_rc#installation--usage)
5. In Home Assistant go to the `Configuration` -> `Integrations` -> `Add integration`
6. Find and select `Prana Recuperators` in the integrations list
7. Follow the instructions to connect to Prana RC server. You will be asked for IP address and port. Keep it as it is if you run Prana RC locally.
8. Once configured hub open `Options` for newly added integration and follow either Discovery flow (default) or choose "Add device manually" if discovery doesn't detect your device for some reason. 
9. Make sure to set a meaningful name for the device as it will be used for both the entity id and user-facing name of your entities.

## Limitations

- Brightness control is not implemented now (read-only)
- Separate flows management is not yet implemented (read-only)

## Credits
* Dmitry Berezovsky, author
* Prana RC, interfacing library to communicate with Prana hardware via BLE.

## Disclaimer
This module is licensed under GPL v3. This means you are free to use in non-commercial projects.

The GPL license clearly explains that there is no warranty for this free software. Please see the included LICENSE file for details.
