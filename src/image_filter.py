from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageStat, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MIN_WIDTH = 180
MIN_HEIGHT = 180
MIN_SHARPNESS = 18.0
MIN_BRIGHTNESS = 22.0
MAX_BRIGHTNESS = 235.0
MIN_CONTRAST = 14.0
MIN_FUNDUS_SCORE = 0.58


@dataclass
class ImageEligibilityResult:
    allowed: bool
    status: str
    reason: str
    score: float
    details: dict


def assess_image_eligibility(image_path: str) -> ImageEligibilityResult:
    path = Path(image_path)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return _reject("unsupported_file_type", "Only JPG, PNG, BMP, or WEBP images are supported.", 0.0)

    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            image = img.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        return _reject("unreadable_image", f"The uploaded file could not be read as a valid image: {exc}", 0.0)

    width, height = image.size
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return _reject(
            "low_resolution",
            f"The image is too small for retinal screening ({width}x{height}).",
            0.0,
            {"width": width, "height": height},
        )

    arr = np.asarray(image).astype(np.float32)
    gray = np.asarray(image.convert("L")).astype(np.float32)
    brightness = float(gray.mean())
    contrast = float(gray.std())
    sharpness = _laplacian_variance(gray)

    quality_details = {
        "width": width,
        "height": height,
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "sharpness": round(sharpness, 2),
    }

    if brightness < MIN_BRIGHTNESS:
        return _reject("too_dark", "The image is too dark for reliable screening.", 0.15, quality_details)
    if brightness > MAX_BRIGHTNESS:
        return _reject("too_bright", "The image is too bright or overexposed for reliable screening.", 0.15, quality_details)
    if contrast < MIN_CONTRAST:
        return _reject("low_contrast", "The image has too little contrast for reliable screening.", 0.2, quality_details)
    if sharpness < MIN_SHARPNESS:
        return _reject("blurry_image", "The image appears too blurry for reliable screening.", 0.25, quality_details)

    fundus_score, fundus_details = _fundus_likeness_score(arr)
    details = {**quality_details, **fundus_details}
    if fundus_score < MIN_FUNDUS_SCORE:
        return _reject(
            "not_fundus_scan",
            "The uploaded image does not appear to be a supported retinal/fundus scan.",
            fundus_score,
            details,
        )

    return ImageEligibilityResult(
        allowed=True,
        status="accepted",
        reason="The uploaded image passed basic quality and retinal/fundus eligibility checks.",
        score=round(fundus_score, 3),
        details=details,
    )


def image_filter_rejection_message(result: ImageEligibilityResult) -> str:
    lines = [
        "OcuAI Image Eligibility Check",
        "",
        "Screening Status: Image rejected before CNN/multimodal analysis",
        "",
        f"Reason: {result.reason}",
        "",
        "Why this matters:",
        "The disease classifier is trained for retinal/fundus scan images. Random photos, screenshots, documents, selfies, or low-quality images can produce unsafe predictions, so OcuCare blocks them before model inference.",
        "",
        "Recommended action:",
        "- Upload a clear retinal/fundus scan image captured for eye screening.",
        "- Avoid screenshots, cropped reports, selfies, phone photos of objects, or heavily blurred images.",
        "- If you have symptoms such as sudden vision loss, severe eye pain, trauma, flashes/floaters, or a curtain-like shadow, seek urgent eye-care evaluation.",
        "",
        f"Eligibility score: {result.score:.2f}",
    ]
    return "\n".join(lines)


def _fundus_likeness_score(arr: np.ndarray) -> tuple:
    red = arr[:, :, 0]
    green = arr[:, :, 1]
    blue = arr[:, :, 2]
    gray = (0.299 * red) + (0.587 * green) + (0.114 * blue)

    non_dark = gray > 18
    non_dark_ratio = float(non_dark.mean())

    red_dominance = float(((red > green * 0.95) & (green > blue * 0.9) & non_dark).mean())
    warm_pixels = float(((red > 55) & (green > 25) & (red > blue * 1.15) & non_dark).mean())
    low_blue_ratio = float(((blue < red * 0.85) & non_dark).mean())
    circularity = _bright_field_circularity(non_dark)
    vessel_like = _vessel_likeness(gray, non_dark)

    score = (
        0.24 * _clip01(red_dominance / 0.42)
        + 0.22 * _clip01(warm_pixels / 0.52)
        + 0.18 * _clip01(low_blue_ratio / 0.58)
        + 0.20 * circularity
        + 0.16 * vessel_like
    )

    details = {
        "fundus_score": round(float(score), 3),
        "non_dark_ratio": round(non_dark_ratio, 3),
        "red_dominance": round(red_dominance, 3),
        "warm_pixel_ratio": round(warm_pixels, 3),
        "low_blue_ratio": round(low_blue_ratio, 3),
        "circular_field_score": round(circularity, 3),
        "vessel_texture_score": round(vessel_like, 3),
    }
    return float(score), details


def _bright_field_circularity(mask: np.ndarray) -> float:
    ys, xs = np.where(mask)
    if len(xs) < 200:
        return 0.0

    height, width = mask.shape
    area_ratio = float(mask.mean())
    bbox_w = max(1, int(xs.max() - xs.min() + 1))
    bbox_h = max(1, int(ys.max() - ys.min() + 1))
    aspect = min(bbox_w, bbox_h) / max(bbox_w, bbox_h)
    fill = len(xs) / float(bbox_w * bbox_h)

    center_x = float(xs.mean())
    center_y = float(ys.mean())
    center_offset = np.sqrt(((center_x - width / 2) / width) ** 2 + ((center_y - height / 2) / height) ** 2)

    return float(
        0.38 * _clip01(area_ratio / 0.45)
        + 0.32 * _clip01((aspect - 0.55) / 0.35)
        + 0.20 * _clip01(fill / 0.62)
        + 0.10 * _clip01(1.0 - center_offset * 3.0)
    )


def _vessel_likeness(gray: np.ndarray, mask: np.ndarray) -> float:
    gy, gx = np.gradient(gray)
    gradient = np.sqrt((gx * gx) + (gy * gy))
    masked_gradient = gradient[mask]
    if masked_gradient.size < 200:
        return 0.0

    p75 = float(np.percentile(masked_gradient, 75))
    p92 = float(np.percentile(masked_gradient, 92))
    texture_band = float(((gradient > p75) & (gradient < max(p92, p75 + 1.0)) & mask).mean())
    return _clip01(texture_band / 0.08)


def _laplacian_variance(gray: np.ndarray) -> float:
    lap = (
        -4 * gray[1:-1, 1:-1]
        + gray[:-2, 1:-1]
        + gray[2:, 1:-1]
        + gray[1:-1, :-2]
        + gray[1:-1, 2:]
    )
    return float(lap.var())


def _reject(status: str, reason: str, score: float, details: dict = None) -> ImageEligibilityResult:
    return ImageEligibilityResult(
        allowed=False,
        status=status,
        reason=reason,
        score=round(float(score), 3),
        details=details or {},
    )


def _clip01(value: float) -> float:
    return float(max(0.0, min(1.0, value)))
