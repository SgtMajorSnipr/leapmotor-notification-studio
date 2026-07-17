from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1] / "leapmotor_notification_studio" / "rootfs" / "app" / "assets" / "vehicles"

JOBS = {
    "t03-white": ("t03-silver", None),
    "b05-white": ("b05-blue", None),
    "b10-white": ("b10-silver", "b10-black"),
    "c10-white": ("c10-graphite", None),
}

POLYGONS = {
    ("t03-white", "hero.png"): [(0.18, .56), (.23, .39), (.36, .27), (.66, .26), (.78, .39), (.82, .62), (.73, .73), (.30, .73)],
    ("t03-white", "top.png"): [(.31, .23), (.69, .23), (.75, .34), (.75, .68), (.68, .80), (.32, .80), (.25, .68), (.25, .34)],
    ("b05-white", "hero.png"): [(.06, .60), (.14, .42), (.34, .27), (.71, .27), (.88, .45), (.89, .66), (.77, .73), (.15, .73)],
    ("b05-white", "top.png"): [(.22, .24), (.78, .24), (.84, .37), (.84, .69), (.73, .79), (.27, .79), (.16, .69), (.16, .37)],
    ("b10-white", "hero.png"): [(.10, .61), (.17, .43), (.35, .30), (.70, .29), (.85, .46), (.86, .64), (.76, .73), (.18, .73)],
    ("b10-white", "top.png"): [(.25, .26), (.75, .26), (.80, .38), (.80, .66), (.71, .76), (.29, .76), (.20, .66), (.20, .38)],
    ("c10-white", "hero.png"): [(.11, .61), (.18, .43), (.36, .29), (.72, .28), (.87, .45), (.88, .65), (.76, .75), (.18, .75)],
    ("c10-white", "top.png"): [(.27, .25), (.73, .25), (.79, .37), (.79, .68), (.70, .78), (.30, .78), (.21, .68), (.21, .37)],
}


def polygon_mask(size, points):
    w, h = size
    mask = Image.new("L", size)
    draw = ImageDraw.Draw(mask)
    draw.polygon([(int(x * w), int(y * h)) for x, y in points], fill=255)
    return np.asarray(mask.filter(ImageFilter.GaussianBlur(max(2, w // 450))), dtype=np.float32) / 255


def recolor(folder, name, source, comparator):
    image = Image.open(ROOT / source / name).convert("RGB")
    rgb = np.asarray(image, dtype=np.float32)
    mx, mn = rgb.max(2), rgb.min(2)
    lum = rgb @ np.array([.2126, .7152, .0722], dtype=np.float32)
    sat = mx - mn
    region = polygon_mask(image.size, POLYGONS[(folder, name)])

    if folder == "b05-white":
        blue = (rgb[:, :, 2] > rgb[:, :, 0] + 3) & (rgb[:, :, 2] > rgb[:, :, 1] - 5) & (sat > 8) & (lum > 24)
        strength = region * np.clip((sat - 6) / 28, 0, 1) * blue
    elif folder == "b10-white" and comparator:
        other = np.asarray(Image.open(ROOT / comparator / name).convert("RGB"), dtype=np.float32)
        delta = np.abs(rgb - other).mean(2)
        candidate = (delta > 9) & (lum > 62) & (sat < 75)
        strength = region * np.clip((delta - 7) / 35, 0, 1) * candidate
    elif folder == "t03-white":
        candidate = (sat < 62) & (lum > 105)
        strength = region * np.clip((lum - 95) / 55, 0, 1) * candidate
    else:
        candidate = (sat < 65) & (lum > 27) & (lum < 205)
        strength = region * np.clip((lum - 22) / 38, 0, 1) * candidate

    strength = np.asarray(Image.fromarray(np.uint8(np.clip(strength, 0, 1) * 255)).filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32) / 255
    white_lum = np.clip(188 + (lum - 45) * .38, 190, 248)
    target = np.stack((white_lum * 1.01, white_lum, white_lum * .985), axis=2)
    alpha = (strength * .94)[:, :, None]
    out = np.clip(rgb * (1 - alpha) + target * alpha, 0, 255).astype(np.uint8)

    destination = ROOT / folder
    destination.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out).save(destination / name, optimize=True)


for destination, (source, comparator) in JOBS.items():
    for filename in ("hero.png", "top.png"):
        recolor(destination, filename, source, comparator)
        print(destination, filename)
