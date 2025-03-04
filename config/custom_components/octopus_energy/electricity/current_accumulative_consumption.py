import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy
)

from homeassistant.util.dt import (now)

from ..coordinators import MultiCoordinatorEntity
from ..coordinators.current_consumption import CurrentConsumptionCoordinatorResult
from .base import (OctopusEnergyElectricitySensor)
from ..utils.attributes import dict_to_typed_dict
from ..utils.rate_information import get_peak_name, get_rate_index, get_unique_rates

from . import calculate_electricity_consumption_and_cost

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCurrentAccumulativeElectricityConsumption(MultiCoordinatorEntity, OctopusEnergyElectricitySensor, RestoreSensor):
  """Sensor for displaying the current accumulative electricity consumption."""

  def __init__(self, hass: HomeAssistant, coordinator, rates_coordinator, standing_charge_coordinator, meter, point, peak_type = None):
    """Init sensor."""
    MultiCoordinatorEntity.__init__(self, coordinator, [rates_coordinator, standing_charge_coordinator])

    self._state = None
    self._last_reset = None
    
    self._rates_coordinator = rates_coordinator
    self._standing_charge_coordinator = standing_charge_coordinator
    self._peak_type = peak_type
    
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return self._is_smart_meter and self._peak_type is None

  @property
  def unique_id(self):
    """The id of the sensor."""
    base_name = f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_current_accumulative_consumption"
    if self._peak_type is not None:
      return f"{base_name}_{self._peak_type}"
    
    return base_name

  @property
  def name(self):
    """Name of the sensor."""
    base_name = f"Current Accumulative Consumption Electricity ({self._serial_number}/{self._mpan})"
    if self._peak_type is not None:
      return f"{get_peak_name(self._peak_type)} {base_name}"

    return base_name

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.ENERGY

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return UnitOfEnergy.KILO_WATT_HOUR

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def last_reset(self):
    """Return the time when the sensor was last reset, if any."""
    return self._last_reset

  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the current days accumulative consumption"""
    current = now()
    consumption_result: CurrentConsumptionCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    consumption_data = consumption_result.data if consumption_result is not None else None
    rate_data = self._rates_coordinator.data.rates if self._rates_coordinator is not None and self._rates_coordinator.data is not None else None
    standing_charge = self._standing_charge_coordinator.data.standing_charge["value_inc_vat"] if self._standing_charge_coordinator is not None and self._standing_charge_coordinator.data is not None and self._standing_charge_coordinator.data.standing_charge is not None else None
    
    target_rate = None
    if current is not None and self._peak_type is not None:
      unique_rates = get_unique_rates(current, rate_data)
      unique_rate_index = get_rate_index(len(unique_rates), self._peak_type)
      target_rate = unique_rates[unique_rate_index] if unique_rate_index is not None else None

    consumption_and_cost = calculate_electricity_consumption_and_cost(
      consumption_data,
      rate_data,
      standing_charge if target_rate is None else 0,
      None, # We want to recalculate
      target_rate=target_rate
    )

    if (consumption_and_cost is not None):
      _LOGGER.debug(f"Calculated previous electricity consumption for '{self._mpan}/{self._serial_number}'...")

      self._state = consumption_and_cost["total_consumption"]
      self._last_reset = consumption_and_cost["last_reset"]

      self._attributes = {
        "mpan": self._mpan,
        "serial_number": self._serial_number,
        "is_export": self._is_export,
        "is_smart_meter": self._is_smart_meter,
        "total": consumption_and_cost["total_consumption"],
        "charges": list(map(lambda charge: {
          "start": charge["start"],
          "end": charge["end"],
          "consumption": charge["consumption"]
        }, consumption_and_cost["charges"]))
      }

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored state: {self._state}')