"""Minimal translation catalogue for rendered dashboard images."""

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "battery": "Battery", "remaining_range": "Remaining range", "last_update": "Last update",
        "vehicle_details": "Vehicle details", "odometer": "Odometer", "lock": "Lock", "cable": "Cable",
        "locked": "Locked", "unlocked": "Unlocked", "connected": "Connected", "disconnected": "Disconnected",
        "parked_safely": "Parked safely", "status": "Status", "parking_location": "Parking location",
        "location_unavailable": "Location unavailable", "charging": "Charging", "not_charging": "Not charging",
        "charging_power": "Charging power", "time_remaining": "Time remaining", "charging_details": "Charging details",
        "charge_limit": "Charge limit", "current": "Current", "voltage": "Voltage", "climate_off": "Climate off",
        "inside_temperature": "Inside temperature", "target_temperature": "Target temperature", "fan_level": "Fan level",
        "level": "Level", "tyre_pressure": "Tyre pressure", "pressure_per_wheel": "Pressure per wheel",
        "front_left": "Front left", "front_right": "Front right", "rear_left": "Rear left", "rear_right": "Rear right",
        "pressures_normal": "All pressures normal", "check_tyre_pressure": "Check tyre pressure",
        "vehicle_security": "Vehicle security", "door_lock": "Door lock", "doors": "Doors", "windows": "Windows",
        "open": "Open", "closed": "Closed", "access_points": "Access points", "boot": "Boot", "sunshade": "Sunshade",
        "vehicle_secured": "Vehicle secured", "attention_required": "Attention required", "unknown": "Unknown",
    },
    "nl": {
        "battery": "Batterij", "remaining_range": "Resterende actieradius", "last_update": "Laatste update",
        "vehicle_details": "Voertuiggegevens", "odometer": "Kilometerstand", "lock": "Slot", "cable": "Kabel",
        "locked": "Vergrendeld", "unlocked": "Ontgrendeld", "connected": "Aangesloten", "disconnected": "Niet aangesloten",
        "parked_safely": "Veilig geparkeerd", "status": "Status", "parking_location": "Parkeerlocatie",
        "location_unavailable": "Locatie onbekend", "charging": "Bezig met laden", "not_charging": "Laadt niet",
        "charging_power": "Laadvermogen", "time_remaining": "Resterende tijd", "charging_details": "Laadgegevens",
        "charge_limit": "Laadlimiet", "current": "Stroom", "voltage": "Spanning", "climate_off": "Klimaat uit",
        "inside_temperature": "Binnentemperatuur", "target_temperature": "Doeltemperatuur", "fan_level": "Ventilatorstand",
        "level": "Niveau", "tyre_pressure": "Bandenspanning", "pressure_per_wheel": "Spanning per wiel",
        "front_left": "Linksvoor", "front_right": "Rechtsvoor", "rear_left": "Linksachter", "rear_right": "Rechtsachter",
        "pressures_normal": "Alle spanningen normaal", "check_tyre_pressure": "Controleer bandenspanning",
        "vehicle_security": "Voertuigbeveiliging", "door_lock": "Portierslot", "doors": "Portieren", "windows": "Ramen",
        "open": "Open", "closed": "Gesloten", "access_points": "Toegangspunten", "boot": "Kofferbak", "sunshade": "Zonnescherm",
        "vehicle_secured": "Voertuig beveiligd", "attention_required": "Aandacht vereist", "unknown": "Onbekend",
    },
}


def t(key: str, language: str = "en") -> str:
    return STRINGS.get(language, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))
