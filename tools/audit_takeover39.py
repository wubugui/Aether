"""Read-only inventory of the inherited candidate and reference identities."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    for relative in ["captures/candidate_opening38/World38.tscn",
                     "captures/candidate_opening38/Game38.tscn"]:
        path = ROOT / relative
        text = path.read_text(encoding="utf8")
        codes = re.findall(r'code = "(.*?)"\n', text, re.S)
        print(relative, sha(path), "embedded shaders", len(codes))
        for i, code in enumerate(codes):
            print(i, len(code), code[:220], "TAIL", code[-650:])
    plan = json.loads((ROOT / "captures/opening_study_38/plan_v5.json").read_text())
    print(json.dumps([{k: p[k] for k in ["ref", "camera", "env"]} for p in plan
                      if p["ref"] in ["1343", "1342", "1274", "1278", "1216"]], indent=2))

if __name__ == "__main__":
    main()
