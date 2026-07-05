# OcuCare Evaluation Toolkit

This folder contains lightweight evaluation assets for defending the research contribution.

The goal is to evaluate OcuCare as a safety-aware ophthalmology support workflow, not only as a chatbot demo.

## What It Tests

- Text-only RAG answers include triage framing and knowledge-base evidence.
- Image-only screening avoids unsupported confident claims.
- Image + symptom screening detects uncertainty or conflict when symptom text may be false.
- Generated outputs can be saved as CSV evidence for the research report.

## Prerequisite

Start the Flask app in another terminal:

```bash
python app.py
```

By default, the evaluation scripts call:

```text
http://127.0.0.1:8080/get
```

Use `--base-url` if the app is running on another port.

## Text-Only RAG Evaluation

```bash
python evaluation/evaluate_text_rag.py
```

Input cases:

```text
evaluation/cases/rag_questions.csv
```

Output:

```text
evaluation/results/rag_eval_results.csv
```

Useful report metrics:

- triage prefix present
- knowledge-base evidence present
- citation markers present
- disclaimer/safety framing present
- required disease terms present

## Image-Only Screening Evaluation

```bash
python evaluation/evaluate_image_screening.py
```

Input cases:

```text
evaluation/cases/image_screening_cases.csv
```

Output:

```text
evaluation/results/image_screening_results.csv
```

Useful report metrics:

- screening language present
- model result present
- uncertainty/unsupported behavior present when needed
- ophthalmologist recommendation present

## Multimodal Fake-Symptom Safety Evaluation

```bash
python evaluation/evaluate_multimodal_safety.py
```

To run both truthful and conflicting symptom variants:

```bash
python evaluation/evaluate_multimodal_safety.py --mode both
```

Input cases:

```text
evaluation/cases/multimodal_conflict_cases.csv
```

Output:

```text
evaluation/results/multimodal_safety_results.csv
```

Useful report metrics:

- uncertainty status present
- conflict/disagreement language present
- image-only evidence shown
- fusion evidence shown
- ophthalmologist recommendation present

## How To Use Results In The Research

Use the generated CSV files to build tables such as:

- OcuCare RAG safety checks across test questions.
- Supported vs uncertain image-only screening outputs.
- Truthful symptoms vs conflicting symptoms in multimodal mode.
- Number of unsafe confident outputs prevented by contradiction detection.

Recommended claim:

> The system improves research defensibility by separating source-grounded text guidance, image-based screening, multimodal agreement, and uncertainty handling.

## Notes

- These scripts do not replace clinical validation.
- The checks are basic safety/behavior checks, not medical correctness scoring.
- Human review is still needed to judge factual correctness and source faithfulness.
- Existing Pinecone records may need re-indexing before page numbers appear in citations.
