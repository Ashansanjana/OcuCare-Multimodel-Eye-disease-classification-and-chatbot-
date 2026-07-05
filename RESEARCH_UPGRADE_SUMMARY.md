# OcuCare Research Upgrade Summary

## Why The Project Needed Improvement

During the research presentation, lecturers raised a valid concern: if a user gives an ophthalmology PDF to Gemini and asks questions, Gemini can already answer many eye-health questions from that document. Therefore, a basic RAG chatbot alone is not enough as a strong research contribution.

Other important concerns were also identified:

- Users may not have fundus or scan images.
- The CNN and multimodal models support only selected disease classes.
- A multimodal model can be misled if the user provides fake or contradictory symptom text.
- The system could sound too confident for a medical setting.
- A four-class classifier may force unsupported cases into one of the known labels.

The project was therefore reframed from:

> An eye disease chatbot with CNN and multimodal classification.

to:

> A safety-aware ophthalmology support workflow that combines source-grounded retrieval, image-based screening, multimodal consistency checking, uncertainty handling, and urgent symptom escalation.

## Revised Research Contribution

The upgraded contribution is not simply that OcuCare answers eye-health questions.

The stronger contribution is that OcuCare separates and evaluates different types of evidence:

- text-only guidance from a curated ophthalmology knowledge base
- image-only screening from the CNN model
- image + symptom fusion from the multimodal model
- image-vs-text consistency checks
- uncertainty and unsupported-case handling
- urgent red-flag symptom escalation

This directly addresses the main lecturer criticism: OcuCare is no longer positioned as just a Gemini PDF wrapper. It is positioned as a controlled, safety-aware ophthalmology decision-support prototype.

## Implemented Improvements

### 1. Text-Only Triage Mode

When a user asks a text-only question without uploading an image, the system now clearly states that image-based screening cannot be performed. It provides educational eye-health triage instead of pretending to diagnose.

Implemented in:

- `app.py`

Key behavior:

- adds text-only triage framing
- detects urgent symptom terms
- clarifies that the response is not a diagnosis

### 2. Source-Grounded RAG Evidence

Text-only chatbot responses now append the retrieved knowledge-base evidence used by the answer.

Implemented in:

- `app.py`
- `src/helper.py`
- `src/prompt.py`

Key behavior:

- retrieves evidence chunks explicitly
- appends a Knowledge Base Evidence section
- preserves PDF source and page metadata for future indexing
- prompts the LLM to cite retrieved chunks with markers such as `[1]`

### 3. Safer Medical Language

The system wording was changed away from definitive diagnosis language.

Examples:

- "diagnosis" -> "screening impression"
- "confidence" -> "model score"
- "diagnostic report" -> "screening support report"

Implemented in:

- `src/prompt.py`
- `app.py`

### 4. Uncertainty Thresholding

The system now avoids confident outputs when model evidence is weak.

Implemented in:

- `app.py`

Checks:

- top model score below threshold
- top two class probabilities too close together
- missing probability distribution

If uncertainty is detected, the system returns an uncertain/unsupported screening response.

### 5. Multimodal Consistency Checking

For image + text inputs, the backend now runs:

1. image-only CNN prediction
2. multimodal fusion prediction
3. consistency comparison

If image-only and fusion results disagree, OcuCare does not return a confident disease report. It returns an uncertain/unsupported result with both evidence sources.

Implemented in:

- `app.py`

This directly answers the lecturer question:

> What happens if a user uploads a real image but enters fake text?

### 6. Urgent Symptom Red-Flag Handling

The system now detects dangerous symptom text such as:

- severe eye pain
- chemical exposure
- trauma
- sudden vision loss
- flashes or floaters
- curtain/shadow over vision
- painful red eye

If urgent symptoms are present, the system escalates the case even if the image model appears normal.

Implemented in:

- `app.py`

This prevents unsafe behavior such as returning a normal-style report when the text describes an emergency.

### 7. Evaluation Toolkit

A new evaluation toolkit was added under:

- `evaluation/`

It includes:

- RAG safety/evidence cases
- image-only screening cases
- multimodal fake-symptom safety cases
- scripts to call the real Flask `/get` endpoint
- a result summarizer that creates a Markdown report

Important files:

- `evaluation/evaluate_text_rag.py`
- `evaluation/evaluate_image_screening.py`
- `evaluation/evaluate_multimodal_safety.py`
- `evaluation/summarize_results.py`
- `evaluation/results_summary.md`

### 8. Research Report And Presentation Materials

Draft research material was added:

- `evaluation/REPORT_EVALUATION_SECTION.md`
- `evaluation/PRESENTATION_OUTLINE.md`
- `RESEARCH_IMPROVEMENT_PLAN.md`

These documents explain the new research contribution, evaluation design, expected results, limitations, and defense strategy.

### 9. Structured Chat UI Rendering

The chatbot frontend now renders model responses into clearer sections instead of one long text block.

Implemented in:

- `templates/chatbot_page.html`
- `static/style.css`

The UI now supports visual sections for:

- screening results
- uncertainty/warnings
- urgent/emergency safety flags
- knowledge-base evidence
- recommendations

It also avoids unsafe direct `innerHTML = data` rendering for bot responses.

## Evaluation Results

The latest generated summary is available in:

`evaluation/results_summary.md`

The expected final result after rerunning all evaluations with the latest urgent-symptom fix is:

| Evaluation | Cases | Expected Passes | Purpose |
| --- | ---: | ---: | --- |
| RAG safety/evidence | 10 | 10 | Checks triage, evidence, citations, and safety language |
| Image-only screening | 5 | 5 | Checks screening language and professional-care recommendation |
| Multimodal fake-text safety | 10 | 10 | Checks conflict, uncertainty, and urgent symptom handling |

Run:

```bash
python evaluation/evaluate_text_rag.py --base-url http://127.0.0.1:5051
python evaluation/evaluate_image_screening.py --base-url http://127.0.0.1:5051
python evaluation/evaluate_multimodal_safety.py --mode both --base-url http://127.0.0.1:5051
python evaluation/summarize_results.py
```

## How To Defend The Project Now

Do not present OcuCare as:

> A chatbot that diagnoses eye disease.

Present it as:

> A bounded, safety-aware ophthalmology support prototype that evaluates source-grounded question answering, image-based screening, multimodal evidence agreement, uncertainty handling, and urgent symptom escalation.

Strong defense points:

- Gemini PDF upload can answer questions, but it does not provide the full controlled workflow implemented here.
- OcuCare separates text-only educational triage from image-based screening.
- OcuCare exposes knowledge-base evidence.
- OcuCare does not blindly trust user symptom text.
- OcuCare detects image-text disagreement.
- OcuCare escalates dangerous symptoms even if image output looks normal.
- OcuCare uses uncertainty handling instead of forcing every case into a disease label.

## Remaining Limitations

These should be stated honestly:

- The system is not clinically validated.
- The image models support only selected classes.
- The CNN and fusion class labels are not fully identical.
- Valid medical eye images are required for image screening.
- User symptom text may be false or incomplete.
- Red-flag detection is rule-based and should be reviewed by clinicians.
- The evaluation scripts check system behavior and safety markers, not full clinical correctness.
- External dataset validation is still needed.

## Recommended Next Improvements

1. Add image quality validation:
   - blur detection
   - brightness check
   - small/low-resolution image warning
   - non-eye image warning

2. Add explainability:
   - Grad-CAM or saliency maps for image predictions

3. Add model comparison:
   - CNN/InceptionV3 vs MobileNet/EfficientNet/ViT

4. Add unsupported/unknown disease detection:
   - avoid forcing unsupported images into the four known classes

5. Add expert review:
   - ophthalmologist or lecturer review of RAG answer correctness and safety

## Final Research Statement

The upgraded OcuCare project investigates how a multimodal medical AI assistant can reduce unsafe or unsupported eye-health responses by combining source-grounded retrieval, image-based screening, multimodal consistency analysis, uncertainty thresholds, and urgent symptom escalation.
