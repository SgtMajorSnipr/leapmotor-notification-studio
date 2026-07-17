"""Vehicle state collection, rendering and notification orchestration."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from aiohttp import ClientSession, ClientTimeout

from home_assistant import HomeAssistantClient
from models import Coordinates, VehicleSnapshot
from renderer import VehicleRenderer
from settings import Settings

LOGGER = logging.getLogger(__name__)


class StudioEngine:
    def __init__(self, ha: HomeAssistantClient, settings: Settings) -> None:
        self.ha = ha
        self.settings = settings
        self.renderer = VehicleRenderer()
        self.last_fingerprint = ""
        self.previous_locked: bool | None = None
        self.last_paths: list[Path] = []
        self.last_error = ""
        self.last_rendered = ""
        self._task: asyncio.Task[None] | None = None
        self._render_lock = asyncio.Lock()

    def update_settings(self, settings: Settings) -> None:
        self.settings = settings
        self.last_fingerprint = ""

    def start(self) -> None:
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        while True:
            try:
                await self.refresh_if_changed()
            except Exception as exc:
                self.last_error = str(exc)
                LOGGER.exception("Refresh failed")
            await asyncio.sleep(self.settings.refresh_interval)

    async def refresh_if_changed(self, force: bool = False) -> list[Path]:
        if not self.settings.entity_prefix:
            return []
        states = await self.ha.state_map()
        relevant = {key: value.get("state") for key, value in states.items() if self.settings.entity_prefix in key}
        fingerprint = hashlib.sha256(json.dumps(relevant, sort_keys=True).encode()).hexdigest()
        if not force and fingerprint == self.last_fingerprint:
            return self.last_paths
        snapshot = await self.snapshot(states)
        async with self._render_lock:
            self.last_paths = await asyncio.to_thread(
                self.renderer.render_all, snapshot, self.settings.car_name, self.settings.vehicle_style,
                self.settings.language, Path(self.settings.output_folder)
            )
        self.last_fingerprint = fingerprint
        self.last_error = ""
        self.last_rendered = snapshot.last_seen
        await self._parking_transition(snapshot)
        LOGGER.info("Rendered %d dashboard images", len(self.last_paths))
        return self.last_paths

    async def snapshot(self, states: dict[str, dict[str, Any]]) -> VehicleSnapshot:
        s = self.settings

        def state(domain: str, suffix: str, default: str = "") -> str:
            return str(states.get(s.entity(domain, suffix), {}).get("state", default))

        def number(domain: str, suffix: str, default: float = 0) -> float:
            try: return float(state(domain, suffix, str(default)))
            except ValueError: return default

        def boolean(domain: str, suffix: str) -> bool:
            return state(domain, suffix).lower() in {"on", "open", "locked", "connected", "charging"}

        tracker = states.get(s.entity("device_tracker", "location"), {})
        attributes = tracker.get("attributes", {})
        coordinates = None
        if attributes.get("latitude") is not None and attributes.get("longitude") is not None:
            coordinates = Coordinates(float(attributes["latitude"]), float(attributes["longitude"]))
        address = next((str(attributes[key]) for key in ("address", "friendly_location", "place_name") if attributes.get(key)), "")
        if not address and coordinates and s.geoapify_api_key:
            address = await self.reverse_geocode(coordinates)
        map_image = await self.fetch_map_image(coordinates) if coordinates and s.geoapify_api_key else None
        tyre = lambda suffix: (lambda value: value / 100 if value > 20 else value)(number("sensor", suffix))
        return VehicleSnapshot(
            battery=number("sensor", "battery"), range_km=number("sensor", "range"),
            odometer_km=number("sensor", "odometer"), state=state("sensor", "state", "Unknown"),
            last_seen=state("sensor", "last_seen", "Unknown"), coordinates=coordinates, address=address,
            map_image=map_image,
            charging=boolean("binary_sensor", "charging"), plug_connected=boolean("binary_sensor", "plug_connected"),
            charge_power=number("sensor", "charge_power"), charge_current=number("sensor", "charge_current"),
            charge_voltage=number("sensor", "charge_voltage"), charge_remaining=state("sensor", "charge_time_remaining", "—"),
            charge_limit=number("number", "charge_limit", 100), inside_temp=number("sensor", "inside_temp"),
            target_temp=number("sensor", "ac_target"), fan_level=number("number", "fan_level"),
            climate=boolean("binary_sensor", "climate"), climate_mode=state("sensor", "climate_mode", "Off"),
            tyre_fl=tyre("tyre_fl"), tyre_fr=tyre("tyre_fr"), tyre_rl=tyre("tyre_rl"), tyre_rr=tyre("tyre_rr"),
            locked=state("lock", "door_lock").lower() == "locked" or boolean("binary_sensor", "locked"),
            any_door=boolean("binary_sensor", "any_door"), any_window=boolean("binary_sensor", "any_window"),
            trunk=boolean("binary_sensor", "trunk"), sunshade=boolean("binary_sensor", "sunshade"))

    async def reverse_geocode(self, coordinates: Coordinates) -> str:
        query = urlencode({"lat": coordinates.latitude, "lon": coordinates.longitude, "apiKey": self.settings.geoapify_api_key})
        async with ClientSession(timeout=ClientTimeout(total=10)) as session:
            async with session.get(f"https://api.geoapify.com/v1/geocode/reverse?{query}") as response:
                response.raise_for_status()
                features = (await response.json()).get("features", [])
        return features[0].get("properties", {}).get("formatted", "") if features else ""

    async def fetch_map_image(self, coordinates: Coordinates) -> bytes | None:
        query = urlencode({
            "style": "dark-matter", "width": 940, "height": 480, "zoom": 15,
            "center": f"lonlat:{coordinates.longitude},{coordinates.latitude}",
            "marker": f"lonlat:{coordinates.longitude},{coordinates.latitude};color:#5cdd97;size:large",
            "apiKey": self.settings.geoapify_api_key,
        }, safe=":,;")
        try:
            async with ClientSession(timeout=ClientTimeout(total=10)) as session:
                async with session.get(f"https://maps.geoapify.com/v1/staticmap?{query}") as response:
                    response.raise_for_status()
                    return await response.read()
        except Exception:
            LOGGER.warning("Map image fetch failed", exc_info=True)
            return None

    def _parked_image_url(self) -> str:
        folder = Path(self.settings.output_folder)
        try:
            relative = folder.relative_to("/media")
        except ValueError:
            relative = Path(folder.name)
        return f"/media/local/{relative.as_posix()}/parked.png"

    async def _parking_transition(self, snapshot: VehicleSnapshot) -> None:
        newly_locked = self.previous_locked is False and snapshot.locked
        self.previous_locked = snapshot.locked
        if not newly_locked or not self.settings.notifications_enabled:
            return
        await asyncio.sleep(self.settings.trigger_delay)
        payload = {"title": f"{self.settings.car_name} is parked", "message": f"{snapshot.battery:.0f}% · {snapshot.range_km:.0f} km", "data": {"image": self._parked_image_url(), "notification_icon": "mdi:car-electric", "channel": "Vehicle", "clickAction": self.settings.dashboard_path, "url": self.settings.dashboard_path}}
        results = await asyncio.gather(*(self.ha.notify(service, payload) for service in self.settings.notify_services), return_exceptions=True)
        for service, result in zip(self.settings.notify_services, results):
            if isinstance(result, Exception): LOGGER.error("Notification to %s failed: %s", service, result)

    def status(self) -> dict[str, Any]:
        return {"configured": bool(self.settings.entity_prefix), "last_rendered": self.last_rendered, "last_error": self.last_error, "images": [path.name for path in self.last_paths]}
