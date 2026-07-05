from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime

from http_client import post_multipart


DEFAULT_CASES = os.path.join("evaluation", "cases", "image_screening_cases.csv")
DEFAULT_OUTPUT = os.path.join("evaluation", "results", "image_screening_results.csv")


def score_response(response: str) -> dict[str, object]:
    lowered = response.lower()
    return {
        "has_screening_language": "screening" in lowered or "model score" in lowered,
        "has_uncertain_status": "uncertain" in lowered or "unsupported" in lowered,
        "has_model_result": "ai screening impression" in lowered or "image-only model evidence" in lowered,
        "has_doctor_recommendation": "ophthalmologist" in lowered or "eye-care professional" in lowered,
        "response_chars": len(response),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate image-only screening behavior through the Flask /get route."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--cases", default=DEFAULT_CASES)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    rows = []
    with open(args.cases, newline="", encoding="utf-8") as file_obj:
        for case in csv.DictReader(file_obj):
            if not os.path.exists(case["image_path"]):
                response = f"Missing image path: {case['image_path']}"
                error = response
            else:
                error = ""
                try:
                    response = post_multipart(
                        args.base_url,
                        "/get",
                        fields={},
                        files={"image": case["image_path"]},
                        timeout=600,
                    )
                except Exception as exc:
                    response = ""
                    error = f"{type(exc).__name__}: {exc}"
            scores = score_response(response)
            passed = bool(scores["has_model_result"]) and bool(scores["has_doctor_recommendation"])
            rows.append({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "case_id": case["case_id"],
                "image_path": case["image_path"],
                "expected_scope": case["expected_scope"],
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
    print(f"Wrote {len(rows)} image screening rows to {args.output}")
    print(f"Basic checks passed: {passed_count}/{len(rows)}")
    return 0 if passed_count == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
