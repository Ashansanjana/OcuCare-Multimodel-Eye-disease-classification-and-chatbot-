# Presentation Outline: Defending the Revised OcuCare Research

## Slide 1: Title

**OcuCare: A Safety-Aware Multimodal Ophthalmology Support System**

Subtitle:

Source-grounded eye-health Q&A, fundus image screening, multimodal consistency checking, and urgent symptom escalation.

## Slide 2: Problem Statement

General LLMs can answer eye-health questions from uploaded PDFs, but this alone is not enough for a research contribution.

Key problems:

- PDF QA alone is similar to Gemini.
- Users may not have scan images.
- Image models support only selected diseases.
- Multimodal systems can be misled by fake symptom text.
- Medical AI outputs can sound too confident.

## Slide 3: Revised Research Aim

To develop and evaluate a bounded ophthalmology support workflow that:

- answers eye-health questions using source-grounded retrieval
- supports image-based screening for selected conditions
- handles text-only symptom triage when no image is available
- detects image-text disagreement in multimodal input
- escalates urgent symptoms instead of giving unsafe normal outputs

## Slide 4: System Components

1. Text-only RAG chatbot
2. CNN image-only screening model
3. InceptionV3 + BERT multimodal fusion model
4. Uncertainty thresholding
5. Image-only vs fusion consistency checking
6. Urgent symptom red-flag detection

## Slide 5: Why This Is Different From Gemini PDF Upload

Gemini PDF upload:

- general-purpose
- answers from uploaded document
- may not expose consistent safety workflow
- does not use local image classifier
- does not compare image and symptom evidence

OcuCare:

- fixed ophthalmology knowledge base
- retrieved evidence shown
- eye-health domain boundary
- text-only triage framing
- image screening support
- multimodal conflict detection
- urgent symptom escalation

## Slide 6: Multimodal Safety Problem

Lecturer challenge:

> What if a user uploads a real image but enters fake or misleading symptoms?

Revised OcuCare behavior:

- runs image-only prediction
- runs image + text fusion prediction
- compares both outputs
- if they disagree, returns uncertain/unsupported result
- if urgent symptom text appears, escalates even if image result is normal

## Slide 7: Evaluation Design

Three evaluation sets:

| Evaluation | Cases | Purpose |
| --- | ---: | --- |
| RAG safety/evidence | 10 | Checks triage, citations, and knowledge-base evidence |
| Image-only screening | 5 | Checks screening language and referral recommendation |
| Multimodal fake-text safety | 10 | Checks conflict, uncertainty, and urgent symptom handling |

## Slide 8: Results

Use the latest table from:

`evaluation/results_summary.md`

Expected result after rerun:

| Evaluation | Cases | Passed |
| --- | ---: | ---: |
| RAG safety/evidence | 10 | 10 |
| Image-only screening | 5 | 5 |
| Multimodal fake-text safety | 10 | 10 |

## Slide 9: Example Safety Case

Case:

- Image and fusion models may indicate Normal.
- User reports severe eye pain after chemical exposure.

Unsafe behavior:

- "Normal" report only.

Revised behavior:

- flags urgent symptom text
- returns uncertain/urgent safety response
- recommends immediate professional care

## Slide 10: Limitations

- Not clinically validated.
- Supports only selected image classes.
- Requires valid medical eye images for image screening.
- Rule-based urgent symptom detection needs clinical review.
- RAG answer correctness needs expert evaluation.
- Larger and external datasets are needed.

## Slide 11: Final Contribution

The main contribution is not a PDF chatbot.

The contribution is:

> A safety-aware ophthalmology support workflow that combines source-grounded retrieval, image screening, multimodal consistency analysis, uncertainty handling, and urgent symptom escalation.

## Slide 12: Future Work

- Add Grad-CAM explainability.
- Add image quality validation.
- Add unsupported/unknown disease detection.
- Expand disease classes.
- Compare CNN with EfficientNet/MobileNet/ViT.
- Conduct expert ophthalmologist evaluation.
