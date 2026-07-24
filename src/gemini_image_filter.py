import json
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_THRESHOLD = 0.75


@dataclass
class GeminiImageCheckResult:
    allowed: bool
    status: str
    reason: str
    confidence: float
    details: dict


def is_gemini_image_check_enabled() -> bool:
    enabled = os.environ.get("GEMINI_IMAGE_CHECK_ENABLED", "false").lower()
    return enabled in ("1", "true", "yes", "on")


def assess_with_gemini_image_check(image_path: str) -> GeminiImageCheckResult:
    if not is_gemini_image_check_enabled():
        return GeminiImageCheckResult(
            allowed=True,
            status="gemini_image_check_disabled",
            reason="Gemini image validation is disabled.",
            confidence=1.0,
            details={},
        )

    if not os.environ.get("GOOGLE_API_KEY"):
        return _fail_open("GOOGLE_API_KEY is not configured.")

    try:
        raw_text = _call_gemini(image_path)
        data = _extract_json_object(raw_text)
        is_fundus = bool(data.get("is_fundus_scan"))
        confidence = _safe_float(data.get("confidence"), default=0.0)
        quality = str(data.get("quality") or "unknown")
        reason = str(data.get("reason") or "Gemini image check completed.")
        threshold = float(os.environ.get("GEMINI_IMAGE_CHECK_THRESHOLD", DEFAULT_THRESHOLD))

        allowed = is_fundus and confidence >= threshold and quality.lower() not in ("reject", "unusable")
        return GeminiImageCheckResult(
            allowed=allowed,
            status="gemini_fundus_accepted" if allowed else "gemini_fundus_rejected",
            reason=reason,
            confidence=confidence,
            details={
                "is_fundus_scan": is_fundus,
                "quality": quality,
                "threshold": threshold,
                "model": os.environ.get("GEMINI_IMAGE_CHECK_MODEL", DEFAULT_MODEL),
            },
        )
    except Exception as exc:
        return _fail_open(f"Gemini image validation could not run: {exc}")


def gemini_image_rejection_message(result: GeminiImageCheckResult) -> str:
    lines = [
        "OcuAI Image Eligibility Check",
        "",
        "Screening Status: Image rejected before CNN/multimodal analysis",
        "",
        f"Reason: {result.reason}",
        "",
        "Patient-facing result:",
        "The uploaded image was not confirmed as a clear retinal/fundus scan by the Gemini image validation step.",
        "",
        "Recommended action:",
        "- Upload a clear retinal/fundus scan captured for eye screening.",
        "- Avoid screenshots, selfies, documents, external eye photos, or unrelated images.",
        "- If symptoms are sudden, painful, or involve vision loss, seek urgent eye-care evaluation.",
        "",
        f"Gemini validation confidence: {result.confidence:.2f}",
    ]
    return "\n".join(lines)


def _call_gemini(image_path: str) -> str:
    prompt = """
You are an image eligibility validator for an ophthalmology research prototype.

Task:
Decide whether the uploaded image is a retinal/fundus scan suitable for downstream eye-disease screening.

Accept only images that clearly show a fundus/retinal scan: circular or oval retinal field, orange/red fundus appearance, visible retinal vessels, and medical scan-like framing.

Reject normal camera photos, selfies, screenshots, documents, reports, external eye photos, random objects, fake/noisy images, and images where the retinal field is not visible.

Return ONLY valid JSON with this exact shape:
{
  "is_fundus_scan": true,
  "confidence": 0.0,
  "quality": "good|usable|reject|unclear",
  "reason": "short patient-friendly reason"
}
"""
    path = Path(image_path)
    mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    model_name = os.environ.get("GEMINI_IMAGE_CHECK_MODEL", DEFAULT_MODEL)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        image_bytes = path.read_bytes()
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt,
            ],
        )
        return str(getattr(response, "text", "") or "")
    except ImportError:
        import google.generativeai as genai
        from PIL import Image

        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, Image.open(path)])
        return str(getattr(response, "text", "") or "")


def _extract_json_object(raw_text: str) -> dict:
    text = str(raw_text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


def _safe_float(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _fail_open(reason: str) -> GeminiImageCheckResult:
    print(f"[GeminiImageCheck] {reason}")
    return GeminiImageCheckResult(
        allowed=True,
        status="gemini_image_check_unavailable",
        reason=reason,
        confidence=1.0,
        details={"fail_open": True},
    )
