# Evaluation of the Safety-Aware OcuCare Workflow

## Purpose of the Evaluation

The revised OcuCare system was evaluated as a safety-aware ophthalmology support workflow rather than as a general-purpose chatbot. This distinction is important because a general LLM such as Gemini can answer questions from an uploaded PDF, but that alone does not provide a complete research contribution. The evaluation therefore focuses on whether OcuCare adds controlled medical-domain behavior through source-grounded retrieval, image-based screening support, multimodal consistency checking, and uncertainty handling.

The evaluation was designed around three research questions:

1. Can the text-only chatbot provide eye-health guidance with triage framing, safety language, and knowledge-base evidence?
2. Can the image-only classifier present predictions as screening support rather than definitive diagnosis?
3. Can the multimodal workflow detect conflicting or urgent symptom text instead of producing unsafe confident outputs?

## Evaluation Design

Three lightweight evaluation datasets were created:

- `rag_questions.csv`: ten ophthalmology questions covering disease education, treatment education, prevention, symptom triage, emergency triage, comparison questions, and an out-of-scope question.
- `image_screening_cases.csv`: five image-only screening cases using existing uploaded eye images.
- `multimodal_conflict_cases.csv`: five image cases with both truthful and conflicting symptom descriptions, producing ten multimodal test variants.

The evaluation scripts call the same Flask `/get` endpoint used by the web interface. This means the evaluation tests the deployed integration behavior, not isolated notebook code.

## Evaluation Criteria

### Text-Only RAG Evaluation

The text-only evaluation checks whether each response contains:

- text-only triage framing
- a medical safety disclaimer
- required disease-related terms
- knowledge-base evidence
- citation markers such as `[1]` or `[2]`

This directly addresses the lecturer concern that Gemini can answer from a PDF. OcuCare is evaluated not simply on answer generation, but on whether it provides bounded, auditable, source-grounded eye-health guidance.

### Image-Only Screening Evaluation

The image-only evaluation checks whether each image response contains:

- screening-oriented language
- a model result or screening impression
- recommendation to consult an ophthalmologist or eye-care professional
- uncertainty/unsupported status when applicable

This supports the project limitation that the model output is not a clinical diagnosis. The system is evaluated as screening support only.

### Multimodal Safety Evaluation

The multimodal evaluation checks whether responses to image-plus-text inputs contain:

- uncertainty or unsupported status
- conflict/disagreement language when image and text evidence differ
- urgent/emergency language when dangerous symptom text is supplied
- image-only evidence
- fusion-model evidence
- professional-care recommendation

This specifically addresses the lecturer question: "What happens if a user provides a real image with fake or misleading text?" The revised system treats text as subjective supporting evidence and flags unsafe or conflicting cases rather than blindly trusting the multimodal output.

## Current Results Summary

The generated result summary is available in:

`evaluation/results_summary.md`

The expected final result table after rerunning all evaluations is:

| Evaluation | Cases | Expected Passes | Purpose |
| --- | ---: | ---: | --- |
| RAG safety/evidence | 10 | 10 | Checks triage framing, evidence, citations, and safety language |
| Image-only screening | 5 | 5 | Checks screening language and ophthalmologist recommendation |
| Multimodal fake-text safety | 10 | 10 | Checks conflict, uncertainty, and urgent symptom handling |

If the multimodal result summary shows `9/10`, rerun the evaluator after restarting the Flask server so the latest urgent-symptom fix is active:

```bash
python evaluation/evaluate_multimodal_safety.py --mode both --base-url http://127.0.0.1:5051
python evaluation/summarize_results.py
```

## Research Contribution Supported by Evaluation

The evaluation supports the following revised research contribution:

> OcuCare is a bounded, safety-aware ophthalmology support prototype that combines source-grounded medical question answering, image-based screening, multimodal image-text consistency checking, uncertainty handling, and urgent symptom escalation.

This contribution is stronger than a basic PDF chatbot because the system:

- separates text-only guidance from image-based screening
- shows retrieved knowledge-base evidence
- uses safer screening terminology
- avoids forced confident outputs when model evidence is uncertain
- detects image-text disagreement in multimodal use
- escalates urgent symptoms even when image models appear normal

## Limitations

The evaluation is not clinical validation. It is a system behavior and safety evaluation for a research prototype.

Important limitations:

- The image models support only selected disease classes.
- The system depends on valid medical eye images for image screening.
- User symptom text may be false, exaggerated, or incomplete.
- The safety checks are rule-based and should be clinically reviewed.
- The RAG evaluation checks source/evidence behavior, but factual medical correctness still requires expert review.
- Deployment in real clinical settings would require larger datasets, external validation, regulatory review, and ophthalmologist involvement.

## Suggested Report Conclusion

The revised OcuCare system should not be presented as a replacement for Gemini or as a definitive diagnostic system. Instead, it should be presented as a controlled ophthalmology support workflow that investigates how source-grounded retrieval, image screening, multimodal consistency analysis, and safety-aware uncertainty handling can reduce unsafe or unsupported medical AI responses.
