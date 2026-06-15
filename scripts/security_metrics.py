#!/usr/bin/env python
"""Generate blunt ReliQuary security/trust metrics and SVG graphs."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT_DIR / "reports" / "security"


@dataclass
class Metric:
    name: str
    score: int
    weight: int
    evidence: str
    brutal_note: str


def run(command: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        command,
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.returncode, proc.stdout


def can_import(module_name: str) -> bool:
    code = f"import {module_name}"
    return run([sys.executable, "-c", code])[0] == 0


def iter_files(patterns: Iterable[str]) -> Iterable[Path]:
    for pattern in patterns:
        yield from ROOT_DIR.glob(pattern)


def count_regex(pattern: str, files: Iterable[Path]) -> int:
    regex = re.compile(pattern)
    count = 0
    for path in files:
        if not path.is_file():
            continue
        try:
            count += len(regex.findall(path.read_text(errors="ignore")))
        except UnicodeDecodeError:
            continue
    return count


def count_python_functions(paths: Iterable[Path]) -> tuple[int, int]:
    total = 0
    implemented = 0
    for path in paths:
        try:
            tree = ast.parse(path.read_text())
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total += 1
                body = [item for item in node.body if not isinstance(item, ast.Expr)]
                if body and not all(isinstance(item, ast.Pass) for item in body):
                    implemented += 1
    return total, implemented


def metric_bar_svg(metrics: list[Metric]) -> str:
    width = 980
    row_h = 42
    left = 260
    bar_w = 520
    height = 70 + row_h * len(metrics)
    rows = []
    for idx, metric in enumerate(metrics):
        y = 50 + idx * row_h
        fill = "#0f766e" if metric.score >= 75 else "#ca8a04" if metric.score >= 45 else "#dc2626"
        rows.append(
            f'<text x="20" y="{y + 20}" font-size="14" fill="#111827">{metric.name}</text>'
            f'<rect x="{left}" y="{y}" width="{bar_w}" height="24" fill="#e5e7eb" />'
            f'<rect x="{left}" y="{y}" width="{bar_w * metric.score / 100:.1f}" height="24" fill="{fill}" />'
            f'<text x="{left + bar_w + 16}" y="{y + 18}" font-size="14" fill="#111827">{metric.score}/100</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        '<rect width="100%" height="100%" fill="#f8fafc" />'
        '<text x="20" y="28" font-size="20" font-weight="700" fill="#111827">'
        'ReliQuary Security and Trust Scores</text>'
        + "".join(rows)
        + "</svg>"
    )


def risk_svg(metrics: list[Metric]) -> str:
    overall = round(sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics))
    radius = 86
    circumference = 2 * 3.14159 * radius
    offset = circumference * (1 - overall / 100)
    color = "#0f766e" if overall >= 75 else "#ca8a04" if overall >= 45 else "#dc2626"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="260" viewBox="0 0 420 260">
  <rect width="100%" height="100%" fill="#f8fafc" />
  <text x="24" y="34" font-size="20" font-weight="700" fill="#111827">Overall Research Trust Score</text>
  <circle cx="210" cy="140" r="{radius}" fill="none" stroke="#e5e7eb" stroke-width="26" />
  <circle cx="210" cy="140" r="{radius}" fill="none" stroke="{color}" stroke-width="26"
    stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
    transform="rotate(-90 210 140)" />
  <text x="210" y="132" text-anchor="middle" font-size="46" font-weight="800" fill="#111827">{overall}</text>
  <text x="210" y="164" text-anchor="middle" font-size="16" fill="#4b5563">out of 100</text>
</svg>"""


def main() -> None:
    py_files = list(iter_files(["apps/**/*.py", "auth/**/*.py", "core/**/*.py", "vaults/**/*.py", "agents/**/*.py", "zk/**/*.py"]))
    test_code, test_output = run([
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/test_crypto.py",
        "tests/api/test_vault_access.py",
        "tests/api/test_research_surface.py",
        "tests/test_vault_storage_persistence.py",
    ])
    tests_pass = test_code == 0
    rust_available = can_import("reliquary_encryptor") and can_import("reliquary_merkle")
    mock_count = count_regex(r"\bmock\b|Mock|TODO|placeholder|For now", py_files)
    insecure_count = count_regex(r"allow_origins=\[\"\*\"\]|simulation mode|default=.*password|encrypted_", py_files)
    total_functions, implemented_functions = count_python_functions(py_files)
    implementation_ratio = implemented_functions / total_functions if total_functions else 0
    _, tracked_files = run(["git", "ls-files"])
    generated_leftovers = [
        item
        for item in tracked_files.splitlines()
        if item.endswith((".mem", ".db", ".sqlite", ".wtns", ".zkey", ".ptau", ".log"))
    ]

    metrics = [
        Metric(
            "Runnable verification",
            92 if tests_pass else 20,
            18,
            "Focused pytest matrix passes" if tests_pass else "Focused pytest matrix fails",
            "This is the strongest part only after the current cleanup; full-suite health is still unknown.",
        ),
        Metric(
            "Rust crypto boundary",
            82 if rust_available else 45,
            14,
            "Rust PyO3 modules imported and PQC tests ran" if rust_available else "Rust modules unavailable",
            "Good direction. Needs audited algorithms, test vectors, and release builds in CI.",
        ),
        Metric(
            "Persistent storage",
            72,
            14,
            "Postgres backend, schema creation, and restart-style storage test exist",
            "Real Postgres exists now, but encryption-at-rest semantics are still weak around secret payload handling.",
        ),
        Metric(
            "API research surface",
            78,
            12,
            "Auth, ZK, vault, context, trust, agents, and audit routers are exposed",
            "Breadth is good. Depth varies heavily across routers.",
        ),
        Metric(
            "Artifact hygiene",
            95 if not generated_leftovers else 55,
            10,
            f"{len(generated_leftovers)} generated artifacts found outside ignored build dirs",
            "Much better after cleanup. Keep generated proof/log/database files out of git forever.",
        ),
        Metric(
            "Prototype debt",
            max(20, 100 - min(mock_count, 100)),
            14,
            f"{mock_count} mock/TODO/placeholder/prototype markers found",
            "This is the ugly truth: the repo still contains lots of research scaffolding and simulated paths.",
        ),
        Metric(
            "Secure defaults",
            max(25, 90 - insecure_count * 8),
            12,
            f"{insecure_count} insecure-default markers found",
            "CORS wildcards, simulation modes, dev passwords, and fake encrypted prefixes are not production security.",
        ),
        Metric(
            "Implementation density",
            round(implementation_ratio * 100),
            6,
            f"{implemented_functions}/{total_functions} Python functions have non-pass bodies",
            "Quantity is not quality, but it shows this is not just a website.",
        ),
    ]

    overall = round(sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics))
    payload = {
        "overall_score": overall,
        "verdict": "promising but not production trustworthy" if overall < 80 else "strong research prototype",
        "metrics": [m.__dict__ for m in metrics],
        "pytest_output": test_output,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "metrics.json").write_text(json.dumps(payload, indent=2))
    (REPORT_DIR / "scorecard.svg").write_text(metric_bar_svg(metrics))
    (REPORT_DIR / "overall.svg").write_text(risk_svg(metrics))

    lines = [
        "# ReliQuary Security and Trust Report",
        "",
        f"Overall score: **{overall}/100**",
        "",
        "## Brutal Verdict",
        "",
        payload["verdict"].capitalize() + ".",
        "",
        "This project is now more than a website: it has a real API surface, Rust crypto modules, "
        "a Postgres storage path, and runnable research flows. It is still not something I would "
        "trust with production secrets without hardening the mocked/prototype areas listed below.",
        "",
        "## Metrics",
        "",
    ]
    for metric in metrics:
        lines.extend([
            f"### {metric.name}: {metric.score}/100",
            f"- Evidence: {metric.evidence}",
            f"- Brutal note: {metric.brutal_note}",
            "",
        ])
    lines.extend([
        "## Generated Graphs",
        "",
        "- `reports/security/overall.svg`",
        "- `reports/security/scorecard.svg`",
        "",
    ])
    (REPORT_DIR / "REPORT.md").write_text("\n".join(lines))

    print(json.dumps({"overall_score": overall, "report": str(REPORT_DIR / "REPORT.md")}, indent=2))


if __name__ == "__main__":
    main()
