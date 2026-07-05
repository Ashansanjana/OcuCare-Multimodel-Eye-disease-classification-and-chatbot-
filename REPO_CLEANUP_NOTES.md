# Repository Cleanup Notes

## Cleanup Completed

Generated artifacts removed:

- root `__pycache__/`
- `src/__pycache__/`
- `evaluation/__pycache__/`
- temporary `eval-server.log`
- temporary `eval-server.err.log`
- offline-check evaluation CSVs

Generated evaluation result CSVs are kept locally but ignored by Git:

- `evaluation/results/rag_eval_results.csv`
- `evaluation/results/image_screening_results.csv`
- `evaluation/results/multimodal_safety_results.csv`

These are useful for presentation/report evidence, but they do not need to be committed unless a submission specifically asks for raw results.

## Files That Belong To The Research Upgrade

Core backend changes:

- `app.py`
- `src/helper.py`
- `src/prompt.py`

Frontend/UI changes:

- `templates/chatbot_page.html`
- `static/style.css`

Evaluation toolkit:

- `evaluation/README.md`
- `evaluation/http_client.py`
- `evaluation/evaluate_text_rag.py`
- `evaluation/evaluate_image_screening.py`
- `evaluation/evaluate_multimodal_safety.py`
- `evaluation/summarize_results.py`
- `evaluation/cases/rag_questions.csv`
- `evaluation/cases/image_screening_cases.csv`
- `evaluation/cases/multimodal_conflict_cases.csv`
- `evaluation/results_summary.md`

Research documentation:

- `RESEARCH_IMPROVEMENT_PLAN.md`
- `RESEARCH_UPGRADE_SUMMARY.md`
- `evaluation/REPORT_EVALUATION_SECTION.md`
- `evaluation/PRESENTATION_OUTLINE.md`

Ignore rules:

- `.gitignore` now ignores `evaluation/results/`.

## Files To Review Before Final Submission

These files are modified but are not central to the upgrade work and should be reviewed carefully before submission:

- `eye_diseases_classification_inceptionv3_95.ipynb`
- `multimodel_eye_disease_classification_Final versiom.ipynb`
- `requirements.txt`
- `src/inference.py`
- `.gitignore` entry for `calude.py`

Notes:

- The notebook diffs are very large. They may be notebook output/metadata changes rather than meaningful research changes.
- `requirements.txt` changed from pinned versions to unpinned package names. For reproducible research, pinned versions are usually better.
- `src/inference.py` fallback label changed from `Retinal Disease` to `Diabetic Retinopathy`; the actual JSON label map still controls normal fusion runtime when available.
- The `.gitignore` entry `calude.py` appears unrelated to the OcuCare upgrade.

## Verification Completed

The following syntax verification passed:

```bash
python -m py_compile app.py src/helper.py src/prompt.py src/inference.py evaluation/http_client.py evaluation/evaluate_text_rag.py evaluation/evaluate_image_screening.py evaluation/evaluate_multimodal_safety.py evaluation/summarize_results.py
```

The result summary generator ran successfully:

```bash
python evaluation/summarize_results.py --output evaluation/results_summary.md
```

## Recommended Final Submission Steps

1. Rerun the final evaluation scripts after starting Flask:

```bash
python evaluation/evaluate_text_rag.py --base-url http://127.0.0.1:5051
python evaluation/evaluate_image_screening.py --base-url http://127.0.0.1:5051
python evaluation/evaluate_multimodal_safety.py --mode both --base-url http://127.0.0.1:5051
python evaluation/summarize_results.py
```

2. Check `evaluation/results_summary.md`.

3. Review the notebook diffs before committing or submitting.

4. Decide whether `requirements.txt` should be restored to pinned versions for reproducibility.

5. Copy the relevant sections from:

- `RESEARCH_UPGRADE_SUMMARY.md`
- `evaluation/REPORT_EVALUATION_SECTION.md`
- `evaluation/PRESENTATION_OUTLINE.md`

into the final report and presentation.
