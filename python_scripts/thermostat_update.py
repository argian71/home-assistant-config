"""
Update Z-Wave thermostats (e.g. Danfoss 014G0013) state and current temperature
from external sensor.
Arguments:
 - thermostat			- thermostat entity_id (required)
 - sensor				- sensor entity_id (required)
 - heat_state			- name of heating state, default 'heat' (optional),
                          changing heat_state from the default value will broke
                          compatibility with HomeKit
 - idle_state			- name of idle state, default 'off' (optional),
                          changing idle_state from the default value will broke
                          compatibility with HomeKit
 - idle_heat_temp		- temperature value between 'idle' and 'heat' states,
                          default 8 (optional)
 - state_only           - with state_only set to 'true' script will update only
                          state of the thermostat (optional)

Configuration example:

service: python_script.thermostat_update
data:
  thermostat: climate.thermostat_kitchen
  sensor: sensor.temperature_kitchen
  heat_stat: 'auto'
  idle_state: 'idle'
  idle_heat_temp: 10
  state_only: false

Script supports custom_updater component. Add this to your configuration and
stay up-to-date.

custom_updater:
  track:
    - python_scripts
  python_script_urls:
    - https://raw.githubusercontent.com/bieniu/home-assistant-config/master/python_scripts/python_scripts.json
"""
VERSION = '0.3.1'

ATTR_THERMOSTAT = 'thermostat'
ATTR_SENSOR = 'sensor'
ATTR_HEAT_STATE = 'heat_state'
ATTR_IDLE_STATE = 'idle_state'
ATTR_IDLE_HEAT_TEMP = 'idle_heat_temp'
ATTR_STATE_ONLY = 'state_only'
ATTR_CURRENT_TEMP = 'current_temperature'
ATTR_OPERATION_LIST = 'operation_list'
ATTR_OPERATION_MODE = 'operation_mode'
ATTR_TEMPERATURE = 'temperature'

ATTR_HEAT_STATE_DEFAULT = 'heat'
ATTR_IDLE_STATE_DEFAULT = 'off'
ATTR_IDLE_HEAT_TEMP_DEFAULT = 8
ATTR_STATE_ONLY_DEFAULT = False

thermostat_id = data.get(ATTR_THERMOSTAT)
sensor_id = data.get(ATTR_SENSOR)
heat_state = data.get(ATTR_HEAT_STATE, ATTR_HEAT_STATE_DEFAULT)
idle_state = data.get(ATTR_IDLE_STATE, ATTR_IDLE_STATE_DEFAULT)
idle_heat_temp = float(data.get(ATTR_IDLE_HEAT_TEMP, ATTR_IDLE_HEAT_TEMP_DEFAULT))
state_only = data.get(ATTR_STATE_ONLY, ATTR_STATE_ONLY_DEFAULT)

temp = None

if not thermostat_id:
    logger.error("Expected {} entity_id, got: {}.".format(ATTR_THERMOSTAT,
                                                          thermostat_id))
else:
    thermostat = hass.states.get(thermostat_id)
    if thermostat is None:
        logger.error("Could not get state of {}.".format(thermostat_id))
    else:
        attributes = thermostat.attributes.copy()
        if not state_only:
            if sensor_id:
                try:
                    temp = float(hass.states.get(sensor_id).state)
                except (ValueError, TypeError):
                    logger.error("Could not get state of {}.".format(sensor_id))
                if temp is None:
                    logger.error("Could not get state of {}.".format(sensor_id))
                else:
                    attributes[ATTR_CURRENT_TEMP] = temp
            else:
                logger.error("Expected {} entity_id, got: {}.".format(ATTR_SENSOR,
                                                                      sensor_id))
        attributes[ATTR_OPERATION_LIST] = [heat_state, idle_state]
        if float(attributes[ATTR_TEMPERATURE]) > idle_heat_temp:
            state = heat_state
            attributes[ATTR_OPERATION_MODE] = heat_state
        else:
            state = idle_state
            attributes[ATTR_OPERATION_MODE] = idle_state
        hass.states.set(thermostat_id, state, attributes)
