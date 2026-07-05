from __future__ import annotations

import argparse
import csv
import os
from collections import Counter
from datetime import datetime


DEFAULT_OUTPUT = os.path.join("evaluation", "results_summary.md")
DEFAULT_RESULT_FILES = {
    "RAG safety/evidence": os.path.join("evaluation", "results", "rag_eval_results.csv"),
    "Image-only screening": os.path.join("evaluation", "results", "image_screening_results.csv"),
    "Multimodal fake-text safety": os.path.join("evaluation", "results", "multimodal_safety_results.csv"),
}


def read_rows(path: str) -> list[dict[str, str]]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as file_obj:
        return list(csv.DictReader(file_obj))


def bool_value(value: str) -> bool:
    return str(value).strip().lower() == "true"


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, object]:
    total = len(rows)
    passed = sum(1 for row in rows if bool_value(row.get("passed_basic_checks", "")))
    failed = total - passed
    pass_rate = (passed / total * 100.0) if total else 0.0
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
    }


def summarize_boolean_columns(rows: list[dict[str, str]]) -> list[tuple[str, int, int]]:
    if not rows:
        return []
    ignored = {
        "timestamp",
        "case_id",
        "question",
        "category",
        "expected_urgency",
        "image_path",
        "expected_scope",
        "variant",
        "expected_behavior",
        "response_chars",
        "response_preview",
        "error",
    }
    columns = [
        column
        for column in rows[0].keys()
        if column not in ignored and column != "passed_basic_checks"
    ]
    summary = []
    for column in columns:
        values = [row.get(column, "") for row in rows]
        if all(str(value).strip().lower() in ("true", "false", "") for value in values):
            count = sum(1 for value in values if bool_value(value))
            summary.append((column, count, len(rows)))
    return summary


def failed_cases(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if not bool_value(row.get("passed_basic_checks", ""))]


def category_breakdown(rows: list[dict[str, str]], column: str) -> list[tuple[str, int]]:
    if not rows or column not in rows[0]:
        return []
    counts = Counter(row.get(column, "unknown") or "unknown" for row in rows)
    return sorted(counts.items())


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a Markdown research summary from OcuCare evaluation CSV files."
    )
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--rag", default=DEFAULT_RESULT_FILES["RAG safety/evidence"])
    parser.add_argument("--image", default=DEFAULT_RESULT_FILES["Image-only screening"])
    parser.add_argument("--multimodal", default=DEFAULT_RESULT_FILES["Multimodal fake-text safety"])
    args = parser.parse_args()

    result_files = {
        "RAG safety/evidence": args.rag,
        "Image-only screening": args.image,
        "Multimodal fake-text safety": args.multimodal,
    }
    loaded = {name: read_rows(path) for name, path in result_files.items()}

    overview_rows = []
    for name, rows in loaded.items():
        stats = summarize_rows(rows)
        overview_rows.append([
            name,
            str(stats["total"]),
            str(stats["passed"]),
            str(stats["failed"]),
            f"{stats['pass_rate']:.1f}%",
        ])

    lines = [
        "# OcuCare Evaluation Results Summary",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Overall Results",
        "",
        markdown_table(
            ["Evaluation", "Cases", "Passed", "Failed", "Pass Rate"],
            overview_rows,
        ),
        "",
        "## Research Interpretation",
        "",
        "- The RAG evaluation checks whether text-only answers include triage framing, safety language, required disease terms, and knowledge-base evidence.",
        "- The image-only evaluation checks whether model outputs are presented as screening support with a professional-care recommendation.",
        "- The multimodal evaluation checks whether conflicting or urgent symptom text is handled as uncertainty or safety escalation rather than a confident diagnosis.",
        "",
        "These checks support the revised research claim that OcuCare is not only a PDF chatbot, but a safety-aware ophthalmology support workflow with source evidence, screening uncertainty, and multimodal conflict handling.",
        "",
    ]

    for name, rows in loaded.items():
        stats = summarize_rows(rows)
        lines.extend([
            f"## {name}",
            "",
            f"Cases evaluated: {stats['total']}",
            f"Passed basic checks: {stats['passed']}",
            f"Failed basic checks: {stats['failed']}",
            "",
        ])

        boolean_summary = summarize_boolean_columns(rows)
        if boolean_summary:
            lines.extend([
                "### Safety/Behavior Checks",
                "",
                markdown_table(
                    ["Check", "True Count", "Total"],
                    [[check, str(count), str(total)] for check, count, total in boolean_summary],
                ),
                "",
            ])

        for column in ("category", "expected_scope", "variant"):
            breakdown = category_breakdown(rows, column)
            if breakdown:
                lines.extend([
                    f"### Breakdown By {column}",
                    "",
                    markdown_table(
                        [column, "Count"],
                        [[label, str(count)] for label, count in breakdown],
                    ),
                    "",
                ])

        failures = failed_cases(rows)
        if failures:
            lines.extend([
                "### Failed Cases To Review",
                "",
                markdown_table(
                    ["Case", "Variant/Category", "Error", "Preview"],
                    [
                        [
                            row.get("case_id", ""),
                            row.get("variant") or row.get("category") or row.get("expected_scope", ""),
                            row.get("error", ""),
                            " ".join(row.get("response_preview", "").split())[:160],
                        ]
                        for row in failures
                    ],
                ),
                "",
            ])
        else:
            lines.extend([
                "### Failed Cases To Review",
                "",
                "No failed cases in this run.",
                "",
            ])

    lines.extend([
        "## Suggested Slide Table",
        "",
        markdown_table(
            ["Evaluation", "Cases", "Passed", "Purpose"],
            [
                ["RAG safety/evidence", str(summarize_rows(loaded["RAG safety/evidence"])["total"]), str(summarize_rows(loaded["RAG safety/evidence"])["passed"]), "Checks triage, evidence, citations, and safety language"],
                ["Image-only screening", str(summarize_rows(loaded["Image-only screening"])["total"]), str(summarize_rows(loaded["Image-only screening"])["passed"]), "Checks screening framing and ophthalmologist recommendation"],
                ["Multimodal fake-text safety", str(summarize_rows(loaded["Multimodal fake-text safety"])["total"]), str(summarize_rows(loaded["Multimodal fake-text safety"])["passed"]), "Checks conflict, uncertainty, and urgent symptom handling"],
            ],
        ),
        "",
    ])

    with open(args.output, "w", encoding="utf-8", newline="\n") as file_obj:
        file_obj.write("\n".join(lines))

    print(f"Wrote evaluation summary to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
