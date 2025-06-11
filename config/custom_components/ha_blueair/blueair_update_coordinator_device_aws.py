"""Blueair device object."""
from __future__ import annotations
import logging

from blueair_api import ModelEnum

from .blueair_update_coordinator import BlueairUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class BlueairUpdateCoordinatorDeviceAws(BlueairUpdateCoordinator):
    """Blueair device object."""
    @property
    def model(self) -> str:
        """Return api package enum of device model."""
        return self.blueair_api_device.model

    @property
    def fan_speed(self) -> int | None | NotImplemented:
        """Return the current fan speed."""
        return self.blueair_api_device.fan_speed

    @property
    def speed_count(self) -> int:
        """Return the max fan speed."""
        if self.blueair_api_device.model == ModelEnum.HUMIDIFIER_H35I:
            return 64
        elif self.blueair_api_device.model in [
            ModelEnum.MAX_211I,
            ModelEnum.MAX_311I,
            ModelEnum.MAX_311I_PLUS,
            ModelEnum.PROTECT_7440I,
            ModelEnum.PROTECT_7470I
        ]:
            return 91
        elif self.blueair_api_device.model == ModelEnum.T10I:
            return 4
        else:
            return 100

    @property
    def is_on(self) -> bool | None | NotImplemented:
        """Return the current fan state."""
        if self.blueair_api_device.standby is None or self.blueair_api_device.standby is NotImplemented:
            return self.blueair_api_device.standby
        else:
            return not self.blueair_api_device.standby

    @property
    def brightness(self) -> int | None | NotImplemented:
        """Return the brightness of this light between 0..255."""
        if self.blueair_api_device.brightness is None or self.blueair_api_device.brightness is NotImplemented:
            return self.blueair_api_device.brightness
        else:
            return round(self.blueair_api_device.brightness / 100 * 255.0, 0)

    @property
    def germ_shield(self) -> bool | None | NotImplemented:
        return self.blueair_api_device.germ_shield

    @property
    def child_lock(self) -> bool | None | NotImplemented:
        return self.blueair_api_device.child_lock

    @property
    def night_mode(self) -> bool | None | NotImplemented:
        return self.blueair_api_device.night_mode

    @property
    def temperature(self) -> int | None | NotImplemented:
        return self.blueair_api_device.temperature

    @property
    def humidity(self) -> int | None | NotImplemented:
        return self.blueair_api_device.humidity

    @property
    def auto_regulated_humidity(self) -> int | None | NotImplemented:
        return self.blueair_api_device.auto_regulated_humidity

    @property
    def voc(self) -> int | None | NotImplemented:
        return self.blueair_api_device.tVOC

    @property
    def pm1(self) -> int | None | NotImplemented:
        pm1 = self.blueair_api_device.pm1
        if pm1 is None or pm1 is NotImplemented:
            return pm1
        return int((pm1 * 100) // 132)

    @property
    def pm10(self) -> int | None | NotImplemented:
        pm10 = self.blueair_api_device.pm10
        if pm10 is None or pm10 is NotImplemented:
            return pm10
        return int((pm10 * 100) // 132)

    @property
    def pm25(self) -> int | None | NotImplemented:
        # pm25 is the more common name for pm2.5.
        pm25 = self.blueair_api_device.pm2_5
        if pm25 is None or pm25 is NotImplemented:
            return pm25
        return int((pm25 * 100) // 132)

    @property
    def co2(self) -> int | None | NotImplemented:
        return NotImplemented

    @property
    def fan_auto_mode(self) -> bool | None | NotImplemented:
        return self.blueair_api_device.fan_auto_mode

    @property
    def wick_dry_mode(self) -> bool | None | NotImplemented:
        return self.blueair_api_device.wick_dry_mode

    @property
    def water_shortage(self) -> bool | None | NotImplemented:
        return self.blueair_api_device.water_shortage

    @property
    def filter_expired(self) -> bool | None | NotImplemented:
        """Returns the current filter status."""
        return NotImplemented

    @property
    def filter_life(self) -> int | None | NotImplemented:
        if self.blueair_api_device.filter_usage_percentage in (NotImplemented, None):
            return self.blueair_api_device.filter_usage_percentage
        return 100 - self.blueair_api_device.filter_usage_percentage

    @property
    def wick_life(self) -> int | None | NotImplemented:
        if self.blueair_api_device.wick_usage_percentage in (NotImplemented, None):
            return self.blueair_api_device.wick_usage_percentage
        return 100 - self.blueair_api_device.wick_usage_percentage

    @property
    def main_mode(self) -> int | None | NotImplemented:
        return self.blueair_api_device.main_mode

    @property
    def heat_temp(self) -> int | None | NotImplemented:
        return self.blueair_api_device.heat_temp

    @property
    def heat_sub_mode(self) -> int | None | NotImplemented:
        return self.blueair_api_device.heat_sub_mode

    @property
    def heat_fan_speed(self) -> int | None | NotImplemented:
        return self.blueair_api_device.heat_fan_speed

    @property
    def cool_sub_mode(self) -> int | None | NotImplemented:
        return self.blueair_api_device.cool_sub_mode

    @property
    def cool_fan_speed(self) -> int | None | NotImplemented:
        return self.blueair_api_device.cool_fan_speed

    @property
    def ap_sub_mode(self) -> int | None | NotImplemented:
        return self.blueair_api_device.ap_sub_mode

    @property
    def fan_speed_0(self) -> int | None | NotImplemented:
        return self.blueair_api_device.fan_speed_0

    @property
    def temperature_unit(self) -> int | None | NotImplemented:
        return self.blueair_api_device.temperature_unit

    async def set_running(self, running) -> None:
        await self.blueair_api_device.set_standby(not running)
        await self.async_request_refresh()

    async def set_brightness(self, brightness) -> None:
        # Convert Home Assistant brightness (0-255) to Abode brightness (0-99)
        # If 100 is sent to Abode, response is 99 causing an error
        await self.blueair_api_device.set_brightness(round(brightness * 100 / 255.0))
        await self.async_request_refresh()

    async def set_germ_shield(self, enabled: bool) -> None:
        await self.blueair_api_device.set_germ_shield(enabled)
        await self.async_request_refresh()

    async def set_night_mode(self, mode) -> None:
        await self.blueair_api_device.set_night_mode(mode)
        await self.async_request_refresh()

    async def set_fan_auto_mode(self, value: bool) -> None:
        await self.blueair_api_device.set_fan_auto_mode(value)
        await self.async_request_refresh()

    async def set_wick_dry_mode(self, value) -> None:
        await self.blueair_api_device.set_wick_dry_mode(value)
        await self.async_request_refresh()

    async def set_auto_regulated_humidity(self, value) -> None:
        await self.blueair_api_device.set_auto_regulated_humidity(value)
        await self.async_request_refresh()

    async def set_main_mode(self, value: int) -> None:
        await self.blueair_api_device.set_main_mode(value)
        await self.async_request_refresh()

    async def set_heat_temp(self, value: int) -> None:
        await self.blueair_api_device.set_heat_temp(value)
        await self.async_request_refresh()

    async def set_heat_sub_mode(self, value: int) -> None:
        await self.blueair_api_device.set_heat_sub_mode(value)
        await self.async_request_refresh()

    async def set_heat_fan_speed(self, value: int) -> None:
        await self.blueair_api_device.set_heat_fan_speed(value)
        await self.async_request_refresh()

    async def set_cool_sub_mode(self, value: int) -> None:
        await self.blueair_api_device.set_cool_sub_mode(value)
        await self.async_request_refresh()

    async def set_cool_fan_speed(self, value: int) -> None:
        await self.blueair_api_device.set_cool_fan_speed(value)
        await self.async_request_refresh()

    async def set_ap_sub_mode(self, value: int) -> None:
        await self.blueair_api_device.set_main_mode(value)
        await self.async_request_refresh()

    async def set_fan_speed_0(self, value: int) -> None:
        await self.blueair_api_device.set_fan_speed_0(value)
        await self.async_request_refresh()
