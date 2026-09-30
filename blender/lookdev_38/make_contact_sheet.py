"""Build one labeled comparison sheet for all 20 reference scenes."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent / "final" / "all_20_reference_vs_scene.png"
IDS = [
    "1125", "1126", "1128", "1129", "1131", "1135", "1216", "1217",
    "1218", "1220", "1274", "1275", "1276", "1278", "1332", "1341",
    "1342", "1343", "1344", "1347",
]

TILE_W, TILE_H = 520, 293
GAP = 10
CARD_PAD = 16
CARD_W = TILE_W * 2 + GAP + CARD_PAD * 2
CARD_H = 355
COLS = 4
GRID_GAP = 18
MARGIN = 28
HEADER_H = 104
ROWS = len(IDS) // COLS
SHEET_W = MARGIN * 2 + CARD_W * COLS + GRID_GAP * (COLS - 1)
SHEET_H = HEADER_H + MARGIN + CARD_H * ROWS + GRID_GAP * (ROWS - 1) + MARGIN

FONT_PATH = Path("C:/Windows/Fonts/msyh.ttc")
TITLE = ImageFont.truetype(str(FONT_PATH), 36)
LABEL = ImageFont.truetype(str(FONT_PATH), 23)
SMALL = ImageFont.truetype(str(FONT_PATH), 18)


def contained(path):
    with Image.open(path) as source:
        image = source.convert("RGB")
    image.thumbnail((TILE_W, TILE_H), Image.Resampling.LANCZOS)
    tile = Image.new("RGB", (TILE_W, TILE_H), (35, 42, 51))
    tile.paste(image, ((TILE_W - image.width) // 2, (TILE_H - image.height) // 2))
    return tile


def main():
    missing = []
    for scene_id in IDS:
        for path in (ROOT / "ref" / f"{scene_id}.png", OUTPUT.parent / f"{scene_id}.png"):
            if not path.is_file():
                missing.append(str(path))
    if missing:
        raise FileNotFoundError("Missing files:\n" + "\n".join(missing))

    sheet = Image.new("RGB", (SHEET_W, SHEET_H), (21, 27, 34))
    draw = ImageDraw.Draw(sheet)
    draw.text((MARGIN, 17), "飞艇场景预研｜20 张参考与当前结构图", font=TITLE, fill=(241, 246, 250))
    draw.text((MARGIN, 66), "每组左：参考图    右：当前场景渲染", font=SMALL, fill=(166, 185, 201))

    for index, scene_id in enumerate(IDS):
        col, row = index % COLS, index // COLS
        x = MARGIN + col * (CARD_W + GRID_GAP)
        y = HEADER_H + MARGIN + row * (CARD_H + GRID_GAP)
        draw.rounded_rectangle((x, y, x + CARD_W - 1, y + CARD_H - 1), radius=12, fill=(39, 48, 59))
        draw.text((x + CARD_PAD, y + 8), scene_id, font=LABEL, fill=(255, 216, 139))
        draw.text((x + CARD_PAD + 85, y + 10), "参考图", font=SMALL, fill=(188, 207, 219))
        draw.text((x + CARD_PAD + TILE_W + GAP + 12, y + 10), "当前结构图", font=SMALL, fill=(188, 207, 219))

        tile_y = y + 45
        sheet.paste(contained(ROOT / "ref" / f"{scene_id}.png"), (x + CARD_PAD, tile_y))
        sheet.paste(contained(OUTPUT.parent / f"{scene_id}.png"), (x + CARD_PAD + TILE_W + GAP, tile_y))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT, optimize=True)
    print(f"{OUTPUT} ({SHEET_W}x{SHEET_H})")


if __name__ == "__main__":
    main()
