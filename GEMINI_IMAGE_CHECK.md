# Gemini Image Check Filter

OcuCare can optionally use Gemini Vision as a final image eligibility check before CNN or multimodal disease inference.

## Pipeline

```text
Uploaded image
  -> local rule-based filter
  -> local fundus feature-profile filter
  -> Gemini image check
  -> CNN / multimodal model
```

Gemini is not used for disease diagnosis here. It only answers:

```text
Is this image a retinal/fundus scan suitable for screening?
```

## Enable

Add this to `.env`:

```env
GEMINI_IMAGE_CHECK_ENABLED=true
GEMINI_IMAGE_CHECK_MODEL=gemini-2.5-flash
GEMINI_IMAGE_CHECK_THRESHOLD=0.75
```

It uses the existing:

```env
GOOGLE_API_KEY=your_google_api_key
```

## Behavior

Gemini returns JSON:

```json
{
  "is_fundus_scan": true,
  "confidence": 0.92,
  "quality": "usable",
  "reason": "The image shows a retinal field with visible vessel patterns."
}
```

The image is rejected if:

- `is_fundus_scan` is false
- confidence is below `GEMINI_IMAGE_CHECK_THRESHOLD`
- quality is `reject` or `unusable`

## Default Safety

The filter is disabled by default:

```env
GEMINI_IMAGE_CHECK_ENABLED=false
```

If Gemini is unavailable, the checker fails open so the existing local filters continue to protect the app during demos.

## Research Explanation

Use this sentence:

> OcuCare uses a hybrid eligibility gate before image classification: deterministic local image checks, a CNN feature-profile similarity filter, and optional Gemini Vision validation to confirm that the upload is a retinal/fundus scan rather than an unrelated image.

## Notes

Gemini adds API cost and latency, so it should run after local filters, not before them.
