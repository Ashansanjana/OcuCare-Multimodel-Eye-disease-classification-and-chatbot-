import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.image_filter import assess_image_eligibility


RESULTS_DIR = Path("evaluation/results")
OUTPUT_PATH = RESULTS_DIR / "image_filter_results.csv"


def _make_blank(path: Path):
    Image.new("RGB", (256, 256), (255, 255, 255)).save(path)


def _make_document_like(path: Path):
    img = Image.new("RGB", (512, 512), (245, 245, 238))
    draw = ImageDraw.Draw(img)
    for y in range(80, 430, 34):
        draw.rectangle((70, y, 440, y + 7), fill=(40, 40, 40))
    img.save(path)


def _make_synthetic_fundus(path: Path):
    img = Image.new("RGB", (512, 512), (5, 5, 5))
    draw = ImageDraw.Draw(img)
    draw.ellipse((38, 38, 474, 474), fill=(150, 72, 32))
    draw.ellipse((320, 205, 388, 273), fill=(232, 190, 115))
    for endpoint in range(70, 440, 18):
        draw.line((256, 256, endpoint, 90 + (endpoint % 290)), fill=(78, 35, 28), width=3)
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=140))
    img.save(path)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    generated_dir = Path("evaluation/generated_filter_cases")
    generated_dir.mkdir(parents=True, exist_ok=True)

    cases = []
    synthetic_fundus = generated_dir / "synthetic_fundus.png"
    blank = generated_dir / "blank_white.png"
    document = generated_dir / "document_like.png"
    _make_synthetic_fundus(synthetic_fundus)
    _make_blank(blank)
    _make_document_like(document)

    cases.extend([
        ("synthetic_fundus", synthetic_fundus, True),
        ("blank_white", blank, False),
        ("document_like", document, False),
    ])

    uploads = sorted(Path("data/uploads").glob("*"))[:10]
    for path in uploads:
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            cases.append((f"existing_upload_{path.name}", path, True))

    rows = []
    passed = 0
    for name, path, expected_allowed in cases:
        result = assess_image_eligibility(str(path))
        ok = result.allowed == expected_allowed
        passed += int(ok)
        rows.append({
            "case": name,
            "path": str(path),
            "expected_allowed": expected_allowed,
            "actual_allowed": result.allowed,
            "status": result.status,
            "score": result.score,
            "passed": ok,
            "reason": result.reason,
            "details": result.details,
        })

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} image filter rows to {OUTPUT_PATH}")
    print(f"Basic checks passed: {passed}/{len(rows)}")


if __name__ == "__main__":
    main()
