# Haven Lighting Integration

Control your Haven Lighting devices through Home Assistant.

{% if installed %}
## Features

- Automatic discovery of Haven lights
- Support for on/off control
- Brightness control
- Location-based organization

{% if version_installed.replace("v", "").replace(".","") | int < 010  %}
## Breaking Changes

- None at this time
{% endif %}

## Links

- [Documentation](https://github.com/mickeyschwab/haven-hass)
- [Report an issue](https://github.com/mickeyschwab/haven-hass/issues)
{% endif %} 
