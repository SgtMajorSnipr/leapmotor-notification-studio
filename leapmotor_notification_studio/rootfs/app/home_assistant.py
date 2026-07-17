"""Async client for Home Assistant's Supervisor-proxied REST API."""

from __future__ import annotations

import os
from typing import Any

from aiohttp import ClientSession, ClientTimeout


class HomeAssistantClient:
    def __init__(self) -> None:
        token = os.environ.get("SUPERVISOR_TOKEN", "")
        self.base_url = "http://supervisor/core/api"
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        self._session: ClientSession | None = None

    async def start(self) -> None:
        self._session = ClientSession(headers=self.headers, timeout=ClientTimeout(total=20))

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            raise RuntimeError("Home Assistant client has not started")
        return self._session

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def states(self) -> list[dict[str, Any]]:
        async with self.session.get(f"{self.base_url}/states") as response:
            response.raise_for_status()
            return await response.json()

    async def state_map(self) -> dict[str, dict[str, Any]]:
        return {item["entity_id"]: item for item in await self.states()}

    async def services(self) -> list[dict[str, Any]]:
        async with self.session.get(f"{self.base_url}/services") as response:
            response.raise_for_status()
            return await response.json()

    async def notify(self, service: str, payload: dict[str, Any]) -> None:
        service = service.removeprefix("notify.")
        async with self.session.post(f"{self.base_url}/services/notify/{service}", json=payload) as response:
            response.raise_for_status()

    async def discover(self) -> dict[str, list[str]]:
        states = await self.states()
        prefixes: set[str] = set()
        for item in states:
            entity = item["entity_id"].split(".", 1)[-1]
            if entity.endswith("_battery") and "leapmotor" in entity:
                prefixes.add(entity.removesuffix("_battery"))
        services = await self.services()
        notify = sorted(
            f"notify.{name}"
            for domain in services if domain.get("domain") == "notify"
            for name in domain.get("services", {}) if name.startswith("mobile_app_")
        )
        return {"prefixes": sorted(prefixes), "notify_services": notify}
