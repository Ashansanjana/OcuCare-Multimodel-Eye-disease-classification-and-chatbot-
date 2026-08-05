import argparse
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.image_filter import assess_image_eligibility
from src.inference import extract_cnn_embedding


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def collect_images(input_paths: list[Path]) -> list[Path]:
    images = []
    for input_path in input_paths:
        if input_path.is_file() and input_path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(input_path)
        elif input_path.is_dir():
            images.extend(
                path for path in input_path.rglob("*")
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
            )
    return sorted(set(images))


def compute_thresholds(features: np.ndarray, quantile: float, margin: float) -> dict:
    similarities = features @ features.T
    np.fill_diagonal(similarities, -1.0)
    nearest_distances = 1.0 - np.max(similarities, axis=1)

    centroid = features.mean(axis=0)
    centroid = centroid / max(float(np.linalg.norm(centroid)), 1e-8)
    centroid_distances = 1.0 - (features @ centroid)

    knn_threshold = float(np.quantile(nearest_distances, quantile) * margin)
    centroid_threshold = float(np.quantile(centroid_distances, quantile) * margin)

    return {
        "centroid": centroid.astype(np.float32),
        "nearest_distances": nearest_distances.astype(np.float32),
        "centroid_distances": centroid_distances.astype(np.float32),
        "knn_threshold": max(knn_threshold, 0.02),
        "centroid_threshold": max(centroid_threshold, 0.04),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build a no-training fundus feature profile from valid retinal images."
    )
    parser.add_argument(
        "--input",
        nargs="+",
        required=True,
        help="One or more folders/files containing valid fundus images.",
    )
    parser.add_argument(
        "--output",
        default="models/image_filter/fundus_feature_profile.npz",
        help="Output .npz profile path.",
    )
    parser.add_argument("--max-images", type=int, default=1500)
    parser.add_argument("--quantile", type=float, default=0.98)
    parser.add_argument("--margin", type=float, default=1.20)
    parser.add_argument(
        "--skip-rule-filter",
        action="store_true",
        help="Use all readable images, even if the rule-based image filter rejects them.",
    )
    args = parser.parse_args()

    input_paths = [Path(item) for item in args.input]
    image_paths = collect_images(input_paths)
    if args.max_images > 0:
        image_paths = image_paths[:args.max_images]

    if len(image_paths) < 5:
        raise SystemExit("Need at least 5 valid fundus images to build a useful profile.")

    accepted_paths = []
    rows = []
    features = []

    for index, path in enumerate(image_paths, 1):
        rule_result = assess_image_eligibility(str(path))
        if not args.skip_rule_filter and not rule_result.allowed:
            rows.append({
                "path": str(path),
                "used": False,
                "status": rule_result.status,
                "reason": rule_result.reason,
            })
            continue

        try:
            embedding = extract_cnn_embedding(str(path))
            features.append(embedding)
            accepted_paths.append(path)
            rows.append({
                "path": str(path),
                "used": True,
                "status": rule_result.status,
                "reason": rule_result.reason,
            })
            print(f"[{index}/{len(image_paths)}] used {path}")
        except Exception as exc:
            rows.append({
                "path": str(path),
                "used": False,
                "status": "embedding_error",
                "reason": str(exc),
            })
            print(f"[{index}/{len(image_paths)}] skipped {path}: {exc}")

    if len(features) < 5:
        raise SystemExit("Fewer than 5 images produced embeddings. Check input folder and model setup.")

    feature_matrix = np.asarray(features, dtype=np.float32)
    profile = compute_thresholds(feature_matrix, quantile=args.quantile, margin=args.margin)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        features=feature_matrix,
        centroid=profile["centroid"],
        knn_threshold=np.float32(profile["knn_threshold"]),
        centroid_threshold=np.float32(profile["centroid_threshold"]),
        nearest_distances=profile["nearest_distances"],
        centroid_distances=profile["centroid_distances"],
        image_paths=np.asarray([str(path) for path in accepted_paths], dtype=object),
        quantile=np.float32(args.quantile),
        margin=np.float32(args.margin),
    )

    report_path = output_path.with_suffix(".csv")
    with report_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["path", "used", "status", "reason"])
        writer.writeheader()
        writer.writerows(rows)

    print("")
    print(f"Saved fundus feature profile: {output_path}")
    print(f"Saved profile build report: {report_path}")
    print(f"Images used: {len(features)}/{len(image_paths)}")
    print(f"kNN cosine-distance threshold: {profile['knn_threshold']:.4f}")
    print(f"Centroid cosine-distance threshold: {profile['centroid_threshold']:.4f}")


if __name__ == "__main__":
    main()
