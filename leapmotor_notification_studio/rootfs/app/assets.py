"""Image and typography asset helpers."""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent / "assets"


@lru_cache(maxsize=64)
def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "Inter-Bold.ttf" if bold else "Inter-Regular.ttf"
    return ImageFont.truetype(str(ROOT / "fonts" / name), size)


@lru_cache(maxsize=32)
def icon(name: str, size: int) -> Image.Image:
    source = Image.open(ROOT / "icons" / f"{name}.png").convert("RGBA")
    return source.resize((size, size), Image.Resampling.LANCZOS)


def rounded_image(source: Image.Image, size: tuple[int, int], radius: int) -> Image.Image:
    image = source.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    mask = Image.new("L", size)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *size), radius=radius, fill=255)
    image.putalpha(mask)
    return image


def cover_image(path: Path, size: tuple[int, int], radius: int) -> Image.Image:
    source = Image.open(path).convert("RGB")
    ratio = max(size[0] / source.width, size[1] / source.height)
    resized = source.resize((round(source.width * ratio), round(source.height * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return rounded_image(resized.crop((left, top, left + size[0], top + size[1])), size, radius)
