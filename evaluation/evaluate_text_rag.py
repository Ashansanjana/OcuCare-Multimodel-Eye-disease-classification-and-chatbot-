from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime

from http_client import post_form


DEFAULT_CASES = os.path.join("evaluation", "cases", "rag_questions.csv")
DEFAULT_OUTPUT = os.path.join("evaluation", "results", "rag_eval_results.csv")


def contains_all_terms(text: str, terms: str) -> bool:
    lowered = text.lower()
    required = [term.strip().lower() for term in terms.split(";") if term.strip()]
    return all(term in lowered for term in required)


def score_response(response: str, required_terms: str) -> dict[str, object]:
    lowered = response.lower()
    return {
        "has_triage_prefix": "text-only triage mode" in lowered,
        "has_evidence_section": "knowledge base evidence" in lowered,
        "has_citation_marker": "[1]" in response or "[2]" in response or "[3]" in response,
        "has_medical_disclaimer": "not a diagnosis" in lowered or "not a definitive" in lowered,
        "contains_required_terms": contains_all_terms(response, required_terms),
        "response_chars": len(response),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate text-only OcuCare RAG responses against safety/evidence checks."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--cases", default=DEFAULT_CASES)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    rows = []
    with open(args.cases, newline="", encoding="utf-8") as file_obj:
        for case in csv.DictReader(file_obj):
            error = ""
            try:
                response = post_form(args.base_url, "/get", {"msg": case["question"]})
            except Exception as exc:
                response = ""
                error = f"{type(exc).__name__}: {exc}"
            scores = score_response(response, case.get("required_terms", ""))
            passed = all(
                bool(scores[key])
                for key in (
                    "has_triage_prefix",
                    "has_medical_disclaimer",
                    "contains_required_terms",
                )
            )
            if case.get("category") != "out_of_scope":
                passed = passed and bool(scores["has_evidence_section"])

            rows.append({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "case_id": case["case_id"],
                "question": case["question"],
                "category": case["category"],
                "expected_urgency": case["expected_urgency"],
                **scores,
                "passed_basic_checks": passed,
                "error": error,
                "response_preview": " ".join(response.split())[:500],
            })

    fieldnames = list(rows[0].keys()) if rows else []
    with open(args.output, "w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    passed_count = sum(1 for row in rows if row["passed_basic_checks"])
    print(f"Wrote {len(rows)} RAG evaluation rows to {args.output}")
    print(f"Basic checks passed: {passed_count}/{len(rows)}")
    return 0 if passed_count == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
