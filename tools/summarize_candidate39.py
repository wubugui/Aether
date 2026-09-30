"""Bind native/runtime inputs to raw GPU evidence; make a QA contact sheet."""
from pathlib import Path
from hashlib import sha256
import json
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "captures/acceptance39"

def record(path):
    path = Path(path)
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "bytes": path.stat().st_size, "sha256": sha256(path.read_bytes()).hexdigest()}

def main():
    run = OUT / "gpu-c"
    report = json.loads((run / "report.json").read_text(encoding="utf8"))
    for image in report["captures"]:
        assert sha256(Path(image["image"]).read_bytes()).hexdigest() == image["sha256"]
    sources = [ROOT / p for p in ["scripts/game39.gd", "scripts/environment39.gd",
               "scripts/environment39_sky.gdshader", "assets/reference_views39.json",
               "tools/verify_candidate39.gd", "tools/build_candidate39.gd"]]
    sources += list((ROOT / "scenes/candidate39").glob("*.tscn"))
    sources = [p for p in sources if "build" not in p.name]
    issues = []
    for path in [OUT / "gpu-c.stdout.log", OUT / "gpu-c.stderr.log"]:
        for line in path.read_text(encoding="utf8", errors="replace").splitlines():
            if re.search(r"ERROR:|SCRIPT ERROR|WARNING:", line): issues.append(line)
    summary = {"functional_checks_passed": report["passed"], "check_count": len(report["checks"]),
               "full_log_clean": not issues, "log_issues": issues,
               "visual_acceptance": "not_passed", "total_goal_complete": False,
               "sources": [record(p) for p in sources],
               "evidence": [record(p) for p in run.iterdir() if p.is_file()],
               "single_world_instance": len({p["world_instance"] for p in report["captures"]}) == 1,
               "raw_screenshot_count": len(report["captures"]),
               "scope": "Limited native live environment/high-altitude integration. Does not verify all 21 references, complete route, cabin accessibility or full artistic fidelity."}
    (OUT / "summary-c.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf8")
    pairs = [("ref/1343.png", "boot-day.png", "1343 | native normal boot"),
             ("ref/1342.png", "reference-1342.png", "1342 | same live world, moonlight"),
             ("ref/1274.png", "reference-1274.png", "1274 | native cabin A"),
             ("ref/1278.png", "reference-1278.png", "1278 | native cabin B"),
             ("ref/1216.png", "reference-1216.png", "1216 | native cloud sea, weather pending")]
    width, height, label = 640, 360, 27
    sheet = Image.new("RGB", (width*2, (height+label)*len(pairs)+34), "#141b26")
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 9), "LEFT: original reference | RIGHT: actual Game39 GPU | NOT visually accepted", fill="white")
    for i, (source, actual, caption) in enumerate(pairs):
        y = 34+i*(height+label)
        draw.text((12,y+5), caption, fill="#dde8f4")
        for column, path in enumerate([ROOT/source, run/actual]):
            im = Image.open(path).convert("RGB")
            im.thumbnail((width, height))
            sheet.paste(im, (column*width, y+label))
    sheet.save(OUT / "comparison-c.png")
    print(json.dumps({k:summary[k] for k in ["functional_checks_passed","check_count","full_log_clean","raw_screenshot_count","single_world_instance"]}))

if __name__ == "__main__": main()
