import os
from dataclasses import dataclass

import numpy as np


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PROFILE_PATH = os.path.join(BASE_DIR, "models", "image_filter", "fundus_feature_profile.npz")

_profile_cache = None


@dataclass
class FundusFeatureResult:
    allowed: bool
    status: str
    reason: str
    score: float
    details: dict


def assess_fundus_feature_profile(image_path: str, profile_path: str = DEFAULT_PROFILE_PATH) -> FundusFeatureResult:
    profile = _load_profile(profile_path)
    if profile is None:
        return FundusFeatureResult(
            allowed=True,
            status="profile_not_configured",
            reason="Fundus feature profile has not been built yet.",
            score=1.0,
            details={"profile_path": profile_path},
        )

    try:
        from src.inference import extract_cnn_embedding

        embedding = extract_cnn_embedding(image_path)
        features = profile["features"]
        centroid = profile["centroid"]
        knn_threshold = float(profile["knn_threshold"])
        centroid_threshold = float(profile["centroid_threshold"])

        similarities = features @ embedding
        nearest_similarity = float(np.max(similarities))
        knn_distance = float(1.0 - nearest_similarity)
        centroid_distance = float(1.0 - np.dot(centroid, embedding))

        details = {
            "profile_path": profile_path,
            "profile_count": int(features.shape[0]),
            "nearest_similarity": round(nearest_similarity, 4),
            "knn_distance": round(knn_distance, 4),
            "knn_threshold": round(knn_threshold, 4),
            "centroid_distance": round(centroid_distance, 4),
            "centroid_threshold": round(centroid_threshold, 4),
        }

        allowed = knn_distance <= knn_threshold and centroid_distance <= centroid_threshold
        if not allowed:
            return FundusFeatureResult(
                allowed=False,
                status="outside_fundus_feature_profile",
                reason=(
                    "The image is too far from the saved fundus-image feature profile "
                    "built from known retinal images."
                ),
                score=_distance_to_score(knn_distance, knn_threshold),
                details=details,
            )

        return FundusFeatureResult(
            allowed=True,
            status="inside_fundus_feature_profile",
            reason="The image is close to the saved fundus-image feature profile.",
            score=_distance_to_score(knn_distance, knn_threshold),
            details=details,
        )
    except Exception as exc:
        print(f"[FundusFeatureFilter] Failed closed-open due to error: {exc}")
        return FundusFeatureResult(
            allowed=True,
            status="feature_filter_error",
            reason=f"Fundus feature profile check could not run: {exc}",
            score=1.0,
            details={"profile_path": profile_path},
        )


def fundus_feature_rejection_message(result: FundusFeatureResult) -> str:
    lines = [
        "OcuAI Image Eligibility Check",
        "",
        "Screening Status: Image rejected before CNN/multimodal analysis",
        "",
        f"Reason: {result.reason}",
        "",
        "Technical explanation:",
        "OcuCare compared the uploaded image embedding with a saved profile of known retinal/fundus image embeddings. This upload was outside the accepted fundus feature range, so it was blocked before disease prediction.",
        "",
        "Recommended action:",
        "- Upload a clear retinal/fundus scan image captured for eye screening.",
        "- Avoid screenshots, selfies, documents, random phone photos, or unrelated medical images.",
        "- If symptoms are urgent, seek eye-care evaluation instead of relying on image upload.",
        "",
        f"Feature eligibility score: {result.score:.2f}",
    ]
    return "\n".join(lines)


def _load_profile(profile_path: str):
    global _profile_cache
    if _profile_cache and _profile_cache.get("path") == profile_path:
        return _profile_cache
    if not os.path.exists(profile_path):
        return None

    data = np.load(profile_path, allow_pickle=True)
    features = np.asarray(data["features"], dtype=np.float32)
    centroid = np.asarray(data["centroid"], dtype=np.float32)
    features = _normalize_rows(features)
    centroid = _normalize_vector(centroid)

    _profile_cache = {
        "path": profile_path,
        "features": features,
        "centroid": centroid,
        "knn_threshold": float(data["knn_threshold"]),
        "centroid_threshold": float(data["centroid_threshold"]),
    }
    return _profile_cache


def _distance_to_score(distance: float, threshold: float) -> float:
    if threshold <= 0:
        return 0.0
    return float(max(0.0, min(1.0, 1.0 - (distance / (threshold * 1.6)))))


def _normalize_rows(features: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(features, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return features / norms


def _normalize_vector(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm == 0:
        return vector
    return vector / norm
