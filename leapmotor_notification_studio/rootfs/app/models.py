"""Typed domain models."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Coordinates:
    latitude: float
    longitude: float

    @property
    def display(self) -> str:
        return f"{self.latitude:.6f}, {self.longitude:.6f}"


@dataclass(frozen=True, slots=True)
class VehicleSnapshot:
    battery: float = 0
    range_km: float = 0
    odometer_km: float = 0
    state: str = "Unknown"
    last_seen: str = "Unknown"
    coordinates: Coordinates | None = None
    address: str = ""
    charging: bool = False
    plug_connected: bool = False
    charge_power: float = 0
    charge_current: float = 0
    charge_voltage: float = 0
    charge_remaining: str = "—"
    charge_limit: float = 100
    inside_temp: float = 0
    target_temp: float = 0
    fan_level: float = 0
    climate: bool = False
    climate_mode: str = "Off"
    tyre_fl: float = 0
    tyre_fr: float = 0
    tyre_rl: float = 0
    tyre_rr: float = 0
    locked: bool = False
    any_door: bool = False
    any_window: bool = False
    trunk: bool = False
    sunshade: bool = False
