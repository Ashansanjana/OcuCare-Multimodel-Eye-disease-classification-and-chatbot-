# Image Eligibility Filter

OcuCare now checks uploaded images before sending them to the CNN or multimodal fusion model.

## Purpose

The disease classifiers are trained for retinal/fundus scan images. If a user uploads a selfie, screenshot, document, random phone photo, fake image, or very poor-quality image, a disease model may still force a prediction. That is unsafe and weakens the research.

The image eligibility filter blocks unsupported images before model inference.

## Current Implementation

The current filter is deterministic and local. It uses `Pillow` and `NumPy`, which are already project dependencies.

File:

```text
src/image_filter.py
```

Backend integration:

```text
app.py -> /get image upload path -> assess_image_eligibility(filepath)
```

The image reaches `predict_cnn()` or `predict_fusion()` only when the filter returns `allowed=True`.

## No-Training Feature Profile Upgrade

OcuCare also supports a stronger no-training filter:

```text
src/fundus_feature_filter.py
tools/build_fundus_feature_profile.py
```

This profile filter reuses the existing CNN model as a feature extractor. It builds a saved profile from known valid fundus images and then compares each new upload against that profile before disease inference.

Build the profile:

```bash
python tools/build_fundus_feature_profile.py --input data/fundus_profile_source
```

Quick test with existing uploaded fundus images:

```bash
python tools/build_fundus_feature_profile.py --input data/uploads --max-images 300
```

Saved profile:

```text
models/image_filter/fundus_feature_profile.npz
```

If this file exists, the backend automatically applies the feature-distance filter after the rule-based checks.

## Checks

1. File type and readability
   - Supports JPG, JPEG, PNG, BMP, WEBP.
   - Rejects unreadable or corrupted image files.

2. Basic quality
   - Minimum resolution.
   - Brightness range.
   - Contrast threshold.
   - Blur/sharpness threshold.

3. Fundus-likeness
   - Red/orange retinal color dominance.
   - Low-blue fundus-like color profile.
   - Bright circular/oval field estimate.
   - Vessel-like texture estimate.

## Rejection Behavior

Rejected images receive a clear message:

```text
Screening Status: Image rejected before CNN/multimodal analysis
```

The response explains that OcuCare needs a valid retinal/fundus scan and recommends uploading a proper screening image.

## Research Justification

This answers a key safety question:

> What happens if a user uploads an unrelated or fake image?

Answer:

> OcuCare performs an image eligibility check before disease inference. Unsupported or low-quality images are rejected before reaching the CNN or multimodal classifier.

## Future Upgrade

For a stronger final research version, train a binary classifier:

```text
valid fundus image vs invalid/non-fundus image
```

Suggested valid data:

- APTOS
- EyePACS
- Messidor
- ORIGA
- Existing project retinal dataset

Suggested invalid data:

- COCO/ImageNet natural images
- Screenshots
- Documents
- Face/selfie images
- Normal phone camera photos
- AI-generated/fake images

Published fundus quality work such as QuickQual, FundusQ-Net, EyeQ, and FundaQ-8 supports this quality-gating direction.
