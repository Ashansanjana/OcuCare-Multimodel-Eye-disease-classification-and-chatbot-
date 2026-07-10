# No-Training Fundus Feature Profile Filter

This upgrade improves the image filter without training a new model.

Instead of collecting a huge non-fundus dataset, OcuCare builds a profile from known valid retinal/fundus images using the existing CNN model's internal feature vectors.

## Final Upload Pipeline

```text
Uploaded image
  -> rule-based image filter
  -> CNN feature-distance profile filter
  -> CNN or multimodal disease model
```

The CNN/fusion model only receives images that pass both filter layers.

## Why This Works

The disease CNN already learned a fundus-image feature space during training. Images from the same retinal distribution should produce embeddings near other valid fundus images. Random phone photos, documents, screenshots, and unrelated images should usually be farther away.

This is a no-training out-of-distribution style filter:

```text
uploaded image embedding vs saved valid-fundus embedding profile
```

## Step 1: Put Valid Fundus Images In A Folder

Use your existing fundus images only:

```text
data/fundus_profile_source/
  cataract/
  diabetic_retinopathy/
  glaucoma/
  normal/
```

You can also point the script directly at your current dataset folders.

## Step 2: Build The Profile

Example:

```bash
python tools/build_fundus_feature_profile.py --input data/fundus_profile_source
```

For a quick test using existing uploaded images:

```bash
python tools/build_fundus_feature_profile.py --input data/uploads --max-images 300
```

Output:

```text
models/image_filter/fundus_feature_profile.npz
models/image_filter/fundus_feature_profile.csv
```

The `.npz` file is used by the backend. The `.csv` file is a build report showing which images were used.

## Step 3: Run The App

```bash
python app.py
```

When a user uploads an image, OcuCare now runs:

1. basic image quality/validity checks
2. fundus feature profile distance check
3. disease CNN or multimodal model only if accepted

## Runtime Decision

The profile filter calculates:

- nearest fundus embedding distance
- centroid fundus embedding distance

If either distance is too high, the image is rejected before disease analysis.

## Important Notes

- This is not a newly trained classifier.
- It requires only valid fundus images.
- It is stronger than simple color/blur rules.
- It is still not perfect, so keep the rule filter and evaluate with non-fundus test cases.

## Research Explanation

Use this explanation:

> OcuCare uses a hybrid image eligibility gate. First, deterministic image quality checks reject corrupted, low-quality, and obviously unsupported uploads. Second, a no-training embedding-distance filter compares the uploaded image against a saved feature profile generated from known retinal/fundus images using the existing CNN. Images outside the fundus feature distribution are rejected before CNN or multimodal disease inference.
