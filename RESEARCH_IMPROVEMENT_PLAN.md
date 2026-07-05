# OcuCare Research Improvement Plan

## Revised Research Direction

OcuCare should be presented as a bounded ophthalmology decision-support prototype, not as a general chatbot or a replacement for doctors.

Recommended framing:

> A safety-aware ophthalmology support system that combines source-grounded medical question answering, fundus image screening, multimodal image-text evidence fusion, uncertainty handling, and contradiction detection.

## Phase 1: Safety And Research Defensibility

- Add text-only triage framing when no image is provided.
- Show retrieved knowledge-base evidence with chatbot answers.
- Use safer wording: screening support, model score, possible indication.
- Add confidence and margin thresholds for image model outputs.
- Return uncertain/unsupported results instead of forcing a disease label.
- Cross-check image-only and multimodal predictions.
- Flag image/text contradictions instead of trusting symptom text blindly.

## Phase 2: Evaluation Experiments

- Compare OcuCare RAG with Gemini PDF upload on fixed ophthalmology questions.
- Measure answer correctness, citation quality, hallucination rate, refusal quality, and safety warnings.
- Report CNN and fusion confusion matrices, precision, recall, specificity, macro-F1, and per-class performance.
- Test fake symptom robustness:
  - correct image + truthful text
  - correct image + fake/conflicting text
  - image only
  - text only
  - unsupported disease image
- Record how often the new consistency checker prevents unsafe confident outputs.

## Phase 3: Model And Dataset Improvements

- Add or evaluate an unknown/unsupported class.
- Add image quality validation for blur, darkness, resolution, and wrong image type.
- Compare CNN/InceptionV3 against at least one modern baseline such as EfficientNet or MobileNet.
- Add external validation if another dataset is available.
- Add explainability such as Grad-CAM for image predictions.

## Phase 4: Presentation Defense

Key claim:

> The contribution is not that a chatbot can answer from a PDF. The contribution is a controlled, safety-aware workflow that separates text-only guidance, image-based screening, multimodal agreement, and uncertainty handling.

Key limitations to state clearly:

- The image models support only selected disease classes.
- The system requires valid medical eye images for image screening.
- User symptom text may be false or misleading.
- Outputs are educational screening support, not clinical diagnosis.
- Clinical deployment would require expert validation and broader datasets.
