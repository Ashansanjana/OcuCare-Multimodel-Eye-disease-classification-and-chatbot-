import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.inference import predict_cnn, predict_fusion


DEFAULT_PROMPTS = [
    "I have blurry vision and difficulty seeing at night.",
    "I have eye pressure and gradual side vision loss.",
    "I have diabetes and my vision is getting blurry.",
]


def main():
    parser = argparse.ArgumentParser(description="Debug CNN vs multimodal predictions on local images.")
    parser.add_argument("--images", nargs="+", default=None, help="Image paths or folders.")
    parser.add_argument("--max-images", type=int, default=8)
    parser.add_argument("--output", default="evaluation/results/multimodal_debug_results.csv")
    args = parser.parse_args()

    image_paths = collect_images(args.images or ["data/uploads"])[:args.max_images]
    if not image_paths:
        raise SystemExit("No images found.")

    rows = []
    for image_path in image_paths:
        cnn = predict_cnn(str(image_path))
        for prompt in DEFAULT_PROMPTS:
            fusion = predict_fusion(str(image_path), prompt)
            rows.append({
                "image": str(image_path),
                "prompt": prompt,
                "cnn_diagnosis": cnn.get("diagnosis"),
                "cnn_confidence": round(float(cnn.get("confidence", 0.0)), 4),
                "cnn_probs": cnn.get("all_probs"),
                "fusion_diagnosis": fusion.get("diagnosis"),
                "fusion_confidence": round(float(fusion.get("confidence", 0.0)), 4),
                "fusion_probs": fusion.get("all_probs"),
            })
            print(
                f"{image_path.name} | {prompt[:28]}... | "
                f"CNN={cnn.get('diagnosis')} {float(cnn.get('confidence', 0.0)):.1%} | "
                f"Fusion={fusion.get('diagnosis')} {float(fusion.get('confidence', 0.0)):.1%}"
            )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    unique_fusion = sorted({row["fusion_diagnosis"] for row in rows})
    print("")
    print(f"Wrote {len(rows)} rows to {output_path}")
    print(f"Unique fusion predictions: {unique_fusion}")


def collect_images(inputs):
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    images = []
    for item in inputs:
        path = Path(item)
        if path.is_file() and path.suffix.lower() in exts:
            images.append(path)
        elif path.is_dir():
            images.extend(p for p in path.rglob("*") if p.suffix.lower() in exts)
    return sorted(set(images))


if __name__ == "__main__":
    main()
