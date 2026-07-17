"""Aiohttp Ingress application entry point."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from aiohttp import web

from engine import StudioEngine
from home_assistant import HomeAssistantClient
from settings import Settings, VEHICLE_STYLES

WEB = Path(__file__).resolve().parent / "web"
LOGGER = logging.getLogger(__name__)


class StudioApplication:
    def __init__(self) -> None:
        self.settings = Settings.load()
        self.ha = HomeAssistantClient()
        self.engine = StudioEngine(self.ha, self.settings)

    async def start(self, app: web.Application) -> None:
        await self.ha.start()
        self.engine.start()

    async def stop(self, app: web.Application) -> None:
        await self.engine.stop()
        await self.ha.close()

    async def index(self, request: web.Request) -> web.FileResponse:
        return web.FileResponse(WEB / "index.html")

    async def get_settings(self, request: web.Request) -> web.Response:
        return web.json_response(self.settings.public())

    async def catalog(self, request: web.Request) -> web.Response:
        return web.json_response(VEHICLE_STYLES)

    async def save_settings(self, request: web.Request) -> web.Response:
        payload = await request.json()
        if payload.get("geoapify_api_key") == "••••••••":
            payload["geoapify_api_key"] = self.settings.geoapify_api_key
        self.settings = Settings.from_payload(payload)
        self.settings.save()
        self.engine.update_settings(self.settings)
        return web.json_response({"ok": True, "settings": self.settings.public()})

    async def discover(self, request: web.Request) -> web.Response:
        try:
            return web.json_response(await self.ha.discover())
        except Exception as exc:
            LOGGER.exception("Discovery failed")
            raise web.HTTPBadGateway(text=json.dumps({"error": str(exc)}), content_type="application/json") from exc

    async def status(self, request: web.Request) -> web.Response:
        return web.json_response(self.engine.status())

    async def render(self, request: web.Request) -> web.Response:
        try:
            paths = await self.engine.refresh_if_changed(force=True)
            return web.json_response({"ok": True, "images": [path.name for path in paths]})
        except Exception as exc:
            LOGGER.exception("Manual render failed")
            raise web.HTTPBadGateway(text=json.dumps({"error": str(exc)}), content_type="application/json") from exc

    async def image(self, request: web.Request) -> web.StreamResponse:
        name = request.match_info["name"]
        if name not in {"overview", "parked", "charging", "climate", "tyres", "security"}:
            raise web.HTTPNotFound()
        path = Path(self.settings.output_folder) / f"{name}.png"
        if not path.exists():
            raise web.HTTPNotFound(text="Render images first")
        return web.FileResponse(path, headers={"Cache-Control": "no-store"})


def create_app() -> web.Application:
    studio = StudioApplication()
    app = web.Application(client_max_size=2 * 1024 * 1024)
    app["studio"] = studio
    app.router.add_get("/", studio.index)
    app.router.add_get("/api/settings", studio.get_settings)
    app.router.add_get("/api/catalog", studio.catalog)
    app.router.add_put("/api/settings", studio.save_settings)
    app.router.add_get("/api/discover", studio.discover)
    app.router.add_get("/api/status", studio.status)
    app.router.add_post("/api/render", studio.render)
    app.router.add_get("/api/image/{name}.png", studio.image)
    app.router.add_static("/static", WEB, show_index=False)
    app.on_startup.append(studio.start)
    app.on_cleanup.append(studio.stop)
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    web.run_app(create_app(), host="0.0.0.0", port=8099, print=None)
