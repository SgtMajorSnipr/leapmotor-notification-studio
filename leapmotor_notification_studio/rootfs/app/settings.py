"""Persistent, validated application settings."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path("/data/settings.json")
VEHICLE_STYLES = {
    "b10-deep-purple": {"model": "B10", "colour": "Deep Purple"},
    "c10-graphite": {"model": "C10", "colour": "Graphite"},
    "t03-silver": {"model": "T03", "colour": "Silver"},
    "b05-blue": {"model": "B05", "colour": "Metallic Blue"},
}


@dataclass(slots=True)
class Settings:
    car_name: str = "My Leapmotor"
    vehicle_style: str = "b10-deep-purple"
    entity_prefix: str = ""
    notify_services: list[str] = field(default_factory=list)
    dashboard_path: str = "/lovelace/0"
    geoapify_api_key: str = ""
    output_folder: str = "/media/leapmotor-notification-studio"
    notifications_enabled: bool = True
    refresh_interval: int = 30
    trigger_delay: int = 8
    language: str = "en"

    @classmethod
    def load(cls, path: Path = SETTINGS_PATH) -> "Settings":
        if not path.exists():
            return cls()
        values = json.loads(path.read_text(encoding="utf-8"))
        allowed = cls.__dataclass_fields__.keys()
        settings = cls(**{key: value for key, value in values.items() if key in allowed})
        if settings.vehicle_style not in VEHICLE_STYLES:
            settings.vehicle_style = "b10-deep-purple"
        return settings

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Settings":
        settings = cls(**{key: value for key, value in payload.items() if key in cls.__dataclass_fields__})
        settings.car_name = settings.car_name.strip() or "My Leapmotor"
        settings.entity_prefix = settings.entity_prefix.strip().rstrip("_")
        if settings.vehicle_style not in VEHICLE_STYLES:
            settings.vehicle_style = "b10-deep-purple"
        settings.notify_services = list(dict.fromkeys(
            service.strip() for service in settings.notify_services if isinstance(service, str) and service.strip()
        ))
        settings.output_folder = settings.output_folder.strip() or "/media/leapmotor-notification-studio"
        settings.refresh_interval = max(10, min(int(settings.refresh_interval), 3600))
        settings.trigger_delay = max(0, min(int(settings.trigger_delay), 120))
        if settings.language not in {"en", "nl"}:
            settings.language = "en"
        return settings

    def save(self, path: Path = SETTINGS_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        temporary.replace(path)

    def public(self) -> dict[str, Any]:
        values = asdict(self)
        values["geoapify_api_key"] = "" if not self.geoapify_api_key else "••••••••"
        values["has_geoapify_key"] = bool(self.geoapify_api_key)
        return values

    def entity(self, domain: str, suffix: str) -> str:
        return f"{domain}.{self.entity_prefix}_{suffix}" if self.entity_prefix else ""
