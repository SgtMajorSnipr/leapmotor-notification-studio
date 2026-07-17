"""Premium 1080 × 1920 vehicle dashboard renderer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter

from assets import ROOT, cover_image, font, icon, rounded_image
from i18n import t
from models import VehicleSnapshot

SIZE = (1080, 1920)
BACKGROUND = (14, 16, 18)
CARD = (28, 31, 35)
CARD_ALT = (35, 39, 44)
TEXT = (244, 246, 248)
MUTED = (158, 166, 176)
ACCENT = (92, 221, 151)
WARNING = (247, 183, 72)
DANGER = (242, 104, 104)


class Canvas:
    def __init__(self, car_name: str, subtitle: str, hero_path: Path | None = None) -> None:
        self.image = Image.new("RGBA", SIZE, (*BACKGROUND, 255))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.text((64, 64), "LEAPMOTOR", font=font(24, True), fill=ACCENT)
        self.draw.text((64, 102), car_name, font=font(62, True), fill=TEXT)
        self.draw.text((66, 180), subtitle, font=font(30), fill=MUTED)
        self.hero_path = hero_path or ROOT / "vehicles" / "b10-deep-purple" / "hero.png"

    def card(self, box: tuple[int, int, int, int], radius: int = 42) -> None:
        layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        ImageDraw.Draw(layer).rounded_rectangle((box[0], box[1] + 16, box[2], box[3] + 16), radius, fill=(0, 0, 0, 105))
        self.image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(22)))
        self.draw.rounded_rectangle(box, radius, fill=CARD)

    def hero(self) -> None:
        self.card((54, 246, 1026, 718), 48)
        self.image.alpha_composite(cover_image(self.hero_path, (940, 440), 36), (70, 262))

    def rows(self, rows: Iterable[tuple[str, str, str]], start: int = 810) -> None:
        for index, (icon_name, label, value) in enumerate(rows):
            y = start + index * 104
            self.image.alpha_composite(icon(icon_name, 52), (96, y))
            self.draw.text((172, y - 3), label, font=font(32), fill=MUTED)
            value_font = font(38, True)
            width = self.draw.textlength(value, font=value_font)
            self.draw.text((982 - width, y - 8), value, font=value_font, fill=TEXT)

    def status(self, y: int, label: str, value: str, ok: bool, icon_name: str = "location") -> None:
        self.image.alpha_composite(icon(icon_name, 46), (92, y))
        self.draw.text((158, y + 2), label, font=font(30), fill=MUTED)
        value_font = font(32, True)
        width = self.draw.textlength(value, font=value_font)
        self.draw.text((980 - width, y), value, font=value_font, fill=ACCENT if ok else DANGER)

    def compact_rows(self, box: tuple[int, int, int, int], title: str, rows: Iterable[tuple[str, str, str, tuple[int, int, int]]]) -> None:
        x0, y0, x1, y1 = box
        self.draw.text((x0 + 24, y0 + 20), title, font=font(28, True), fill=TEXT)
        rows = list(rows)
        top = y0 + 72
        step = (y1 - 14 - top) / len(rows)
        for index, (icon_name, label, value, color) in enumerate(rows):
            y = int(top + index * step)
            self.image.alpha_composite(icon(icon_name, 32), (x0 + 24, y))
            self.draw.text((x0 + 66, y + 4), label, font=font(22), fill=MUTED)
            value_font = font(25, True)
            width = self.draw.textlength(value, font=value_font)
            self.draw.text((x1 - 24 - width, y + 2), value, font=value_font, fill=color)

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.image.convert("RGB").save(path, "PNG", compress_level=4)
        return path


class VehicleRenderer:
    vehicle_style = "b10-deep-purple"
    language = "en"

    def render_all(self, data: VehicleSnapshot, car_name: str, vehicle_style: str, language: str, folder: Path) -> list[Path]:
        self.vehicle_style = vehicle_style
        self.language = language
        return [method(data, car_name, folder / filename) for method, filename in (
            (self.overview, "overview.png"), (self.parked, "parked.png"),
            (self.charging, "charging.png"), (self.climate, "climate.png"),
            (self.tyres, "tyres.png"), (self.security, "security.png"),
            (self.dashboard_set, "dashboard_set.png"))]

    def base(self, car_name: str, subtitle: str) -> Canvas:
        canvas = Canvas(car_name, subtitle, ROOT / "vehicles" / self.vehicle_style / "hero.png")
        canvas.hero()
        return canvas

    def overview(self, d: VehicleSnapshot, name: str, out: Path) -> Path:
        L = self.language
        c = self.base(name, d.state)
        c.card((54, 754, 1026, 1118)); c.rows((("battery", t("battery", L), f"{d.battery:.0f} %"), ("range", t("remaining_range", L), f"{d.range_km:.0f} km"), ("clock", t("last_update", L), self.time(d.last_seen))))
        c.card((54, 1154, 1026, 1712)); c.draw.text((92, 1200), t("vehicle_details", L), font=font(36, True), fill=TEXT)
        c.status(1300, t("odometer", L), f"{d.odometer_km:,.0f} km".replace(",", "."), True, "range"); c.status(1415, t("lock", L), t("locked", L) if d.locked else t("unlocked", L), d.locked); c.status(1530, t("cable", L), t("connected", L) if d.plug_connected else t("disconnected", L), True, "charge")
        return c.save(out)

    def parked(self, d: VehicleSnapshot, name: str, out: Path) -> Path:
        L = self.language
        c = self.base(name, t("parked_safely", L)); c.card((54, 754, 1026, 1118)); c.rows((("battery", t("battery", L), f"{d.battery:.0f} %"), ("range", t("remaining_range", L), f"{d.range_km:.0f} km"), ("clock", t("status", L), t("locked", L) if d.locked else t("unlocked", L))))
        c.card((54, 1154, 1026, 1712)); c.draw.text((92, 1200), t("parking_location", L), font=font(36, True), fill=TEXT); c.draw.rounded_rectangle((86, 1280, 994, 1628), 34, fill=CARD_ALT)
        location = d.address or (d.coordinates.display if d.coordinates else t("location_unavailable", L)); c.draw.text((130, 1400), self.fit(c, location, 790, 36), font=font(36, True), fill=TEXT)
        return c.save(out)

    def charging(self, d: VehicleSnapshot, name: str, out: Path) -> Path:
        L = self.language
        c = self.base(name, t("charging", L) if d.charging else t("not_charging", L)); c.card((54, 754, 1026, 1118)); c.rows((("battery", t("battery", L), f"{d.battery:.0f} %"), ("charge", t("charging_power", L), f"{d.charge_power:g} kW"), ("clock", t("time_remaining", L), d.charge_remaining)))
        c.card((54, 1154, 1026, 1712)); c.draw.text((92, 1200), t("charging_details", L), font=font(36, True), fill=TEXT); c.status(1300, t("charge_limit", L), f"{d.charge_limit:.0f} %", True, "battery"); c.status(1415, t("current", L), f"{d.charge_current:g} A", True, "charge"); c.status(1530, t("voltage", L), f"{d.charge_voltage:g} V", True, "charge")
        return c.save(out)

    def climate(self, d: VehicleSnapshot, name: str, out: Path) -> Path:
        L = self.language
        c = self.base(name, d.climate_mode if d.climate else t("climate_off", L)); c.card((54, 754, 1026, 1118)); c.rows((("clock", t("inside_temperature", L), f"{d.inside_temp:g} °C"), ("clock", t("target_temperature", L), f"{d.target_temp:g} °C"), ("range", t("fan_level", L), f"{t('level', L)} {d.fan_level:g}")))
        c.card((54, 1154, 1026, 1712)); c.draw.ellipse((390, 1250, 690, 1550), fill=(36, 55, 49), outline=ACCENT if d.climate else MUTED, width=8); text=f"{d.target_temp:g}°"; w=c.draw.textlength(text,font=font(70,True)); c.draw.text((540-w/2,1350),text,font=font(70,True),fill=TEXT)
        return c.save(out)

    def tyres(self, d: VehicleSnapshot, name: str, out: Path) -> Path:
        L = self.language
        c = Canvas(t("tyre_pressure", L), t("pressure_per_wheel", L)); c.card((54, 246, 1026, 1460), 48)
        top = Image.open(ROOT / "vehicles" / self.vehicle_style / "top.png").convert("RGB"); c.image.alpha_composite(rounded_image(top, (620, 1120), 36), (230, 292))
        tyres=((t("front_left", L),d.tyre_fl,(78,410,350,532)),(t("front_right", L),d.tyre_fr,(730,410,1002,532)),(t("rear_left", L),d.tyre_rl,(78,1160,350,1282)),(t("rear_right", L),d.tyre_rr,(730,1160,1002,1282)))
        for label,value,box in tyres:
            color=self.tyre_color(value); c.draw.rounded_rectangle(box,30,fill=CARD_ALT,outline=color,width=4); c.draw.text((box[0]+24,box[1]+20),label,font=font(25),fill=MUTED); c.draw.text((box[0]+24,box[1]+58),f"{value:g} bar",font=font(36,True),fill=color)
        c.card((54,1496,1026,1816)); ok=all(2.2<=v<=2.9 for v in (d.tyre_fl,d.tyre_fr,d.tyre_rl,d.tyre_rr)); c.draw.text((92,1580),t("pressures_normal", L) if ok else t("check_tyre_pressure", L),font=font(42,True),fill=ACCENT if ok else WARNING)
        return c.save(out)

    def security(self, d: VehicleSnapshot, name: str, out: Path) -> Path:
        L = self.language
        has_sunshade = not self.vehicle_style.startswith("t03")
        c=self.base(name,t("vehicle_security", L)); c.card((54,754,1026,1118)); c.rows((("location",t("door_lock", L),t("locked", L) if d.locked else t("unlocked", L)),("location",t("doors", L),t("open", L) if d.any_door else t("closed", L)),("location",t("windows", L),t("open", L) if d.any_window else t("closed", L))))
        c.card((54,1154,1026,1712)); c.draw.text((92,1200),t("access_points", L),font=font(36,True),fill=TEXT); c.status(1300,t("boot", L),t("open", L) if d.trunk else t("closed", L),not d.trunk)
        if has_sunshade: c.status(1415,t("sunshade", L),t("open", L) if d.sunshade else t("closed", L),not d.sunshade)
        safe=d.locked and not d.any_door and not d.any_window and not d.trunk; c.draw.text((355,1580),t("vehicle_secured", L) if safe else t("attention_required", L),font=font(42,True),fill=ACCENT if safe else DANGER)
        return c.save(out)

    def dashboard_set(self, d: VehicleSnapshot, name: str, out: Path) -> Path:
        L = self.language
        has_sunshade = not self.vehicle_style.startswith("t03")
        c = self.base(name, t("full_overview", L))

        battery_rows = [
            ("battery", t("battery", L), f"{d.battery:.0f} %", TEXT),
            ("range", t("remaining_range", L), f"{d.range_km:.0f} km", TEXT),
            ("range", t("odometer", L), f"{d.odometer_km:,.0f} km".replace(",", "."), TEXT),
            ("clock", t("last_update", L), self.time(d.last_seen), MUTED),
        ]
        security_rows = [
            ("location", t("door_lock", L), t("locked", L) if d.locked else t("unlocked", L), ACCENT if d.locked else DANGER),
            ("location", t("doors", L), t("open", L) if d.any_door else t("closed", L), DANGER if d.any_door else ACCENT),
            ("location", t("windows", L), t("open", L) if d.any_window else t("closed", L), DANGER if d.any_window else ACCENT),
            ("location", t("boot", L), t("open", L) if d.trunk else t("closed", L), DANGER if d.trunk else ACCENT),
        ]
        if has_sunshade:
            security_rows.append(("location", t("sunshade", L), t("open", L) if d.sunshade else t("closed", L), DANGER if d.sunshade else ACCENT))
        charging_rows = [
            ("charge", t("status", L), t("charging", L) if d.charging else t("not_charging", L), ACCENT if d.charging else MUTED),
            ("charge", t("charging_power", L), f"{d.charge_power:g} kW", TEXT),
            ("charge", t("current_voltage", L), f"{d.charge_current:g} A · {d.charge_voltage:g} V", TEXT),
            ("battery", t("charge_limit", L), f"{d.charge_limit:.0f} %", TEXT),
            ("clock", t("time_remaining", L), d.charge_remaining, MUTED),
        ]
        climate_rows = [
            ("clock", t("status", L), d.climate_mode if d.climate else t("climate_off", L), ACCENT if d.climate else MUTED),
            ("clock", t("inside_temperature", L), f"{d.inside_temp:g} °C", TEXT),
            ("clock", t("target_temperature", L), f"{d.target_temp:g} °C", TEXT),
            ("range", t("fan_level", L), f"{t('level', L)} {d.fan_level:g}", TEXT),
        ]

        row_h, gap, col_w, col_gap = 353, 20, 474, 24
        x1, x2 = 54, 54 + col_w + col_gap
        y1, y2, y3 = 754, 754 + row_h + gap, 754 + 2 * (row_h + gap)

        c.card((x1, y1, x1 + col_w, y1 + row_h)); c.compact_rows((x1, y1, x1 + col_w, y1 + row_h), t("battery_range", L), battery_rows)
        c.card((x2, y1, x2 + col_w, y1 + row_h)); c.compact_rows((x2, y1, x2 + col_w, y1 + row_h), t("security", L), security_rows)
        c.card((x1, y2, x1 + col_w, y2 + row_h)); c.compact_rows((x1, y2, x1 + col_w, y2 + row_h), t("charging_details", L), charging_rows)
        c.card((x2, y2, x2 + col_w, y2 + row_h)); c.compact_rows((x2, y2, x2 + col_w, y2 + row_h), t("climate", L), climate_rows)

        tyre_box = (x1, y3, x1 + col_w, y3 + row_h)
        c.card(tyre_box)
        c.draw.text((x1 + 24, y3 + 20), t("tyre_pressure", L), font=font(28, True), fill=TEXT)
        chip_w, chip_h, chip_gap = 206, 122, 14
        chip_top = y3 + 74
        chips = (
            (t("front_left", L), d.tyre_fl, x1 + 24, chip_top),
            (t("front_right", L), d.tyre_fr, x1 + 24 + chip_w + chip_gap, chip_top),
            (t("rear_left", L), d.tyre_rl, x1 + 24, chip_top + chip_h + chip_gap),
            (t("rear_right", L), d.tyre_rr, x1 + 24 + chip_w + chip_gap, chip_top + chip_h + chip_gap),
        )
        for label, value, cx, cy in chips:
            color = self.tyre_color(value)
            c.draw.rounded_rectangle((cx, cy, cx + chip_w, cy + chip_h), 22, fill=CARD_ALT, outline=color, width=3)
            c.draw.text((cx + 18, cy + 14), label, font=font(20), fill=MUTED)
            c.draw.text((cx + 18, cy + 44), f"{value:g} bar", font=font(28, True), fill=color)

        location_box = (x2, y3, x2 + col_w, y3 + row_h)
        c.card(location_box)
        c.draw.text((x2 + 24, y3 + 20), t("location", L), font=font(28, True), fill=TEXT)
        place = d.address or (d.coordinates.display if d.coordinates else t("location_unavailable", L))
        c.draw.text((x2 + 24, y3 + 78), self.fit(c, place, col_w - 48, 27), font=font(27, True), fill=TEXT)
        c.draw.text((x2 + 24, y3 + 130), f"{t('status', L)}: {d.state}", font=font(22), fill=MUTED)

        return c.save(out)

    @staticmethod
    def time(value: str) -> str:
        try: return datetime.fromisoformat(value.replace("Z","+00:00")).astimezone().strftime("%d/%m/%Y - %H:%M")
        except (ValueError, AttributeError): return value or "Unknown"

    @staticmethod
    def fit(c: Canvas,text: str,width: int,size: int) -> str:
        f=font(size,True)
        while text and c.draw.textlength(text+"…",font=f)>width: text=text[:-1]
        return text.rstrip()+"…" if text else ""

    @staticmethod
    def tyre_color(value: float) -> tuple[int,int,int]:
        return MUTED if value<=0 else ACCENT if 2.2<=value<=2.9 else WARNING if 1.9<=value<=3.2 else DANGER
