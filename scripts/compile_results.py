"""Compile every *cleared* entry in the results register into one document.

This is the "living document" for the thesis: run it any time (a
supervisor meeting, a milestone, the final submission) to regenerate an
up-to-date compilation of everything that has cleared output checking.
It is generated, not hand-maintained — the source of truth is
docs/results_register.csv plus the actual output files it points to.

Usage
-----
    python scripts/compile_results.py
    python scripts/compile_results.py --status cleared pending_check
    python scripts/compile_results.py --output docs/results_compendium.md

By default only "cleared" outputs are included, since those are the only
ones confirmed safe to circulate outside the secure environment. Use
--status to include drafts too (e.g. for your own working reference while
still on synthetic data).
"""

import argparse
import sys
from pathlib import Path
from collections import defaultdict

# Allow running as `python scripts/compile_results.py` from the repo root
# without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.results_register import read_register
from src.config import REPO_ROOT


def compile_markdown(rows: list, output_path: Path) -> None:
    by_rq = defaultdict(list)
    for row in rows:
        by_rq[row["research_question"] or "(unassigned)"].append(row)

    lines = ["# Results compendium", "", "_Auto-generated from `docs/results_register.csv` — do not edit by hand._", ""]

    for rq in sorted(by_rq):
        lines.append(f"## {rq}")
        lines.append("")
        for row in by_rq[rq]:
            lines.append(f"### {row['output_id']}")
            lines.append("")
            lines.append(f"- **Description:** {row['description']}")
            lines.append(f"- **Status:** {row['status']}")
            lines.append(f"- **Added:** {row['date_added']}")
            lines.append(f"- **Source:** `{row['source']}`")
            if row.get("decision_log_ref"):
                lines.append(f"- **Related decision:** {row['decision_log_ref']}")
            file_path = row.get("file_path", "")
            if file_path:
                resolved = REPO_ROOT / file_path
                if resolved.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg"} and resolved.exists():
                    lines.append(f"\n![{row['output_id']}]({file_path})\n")
                else:
                    lines.append(f"- **File:** `{file_path}`" + ("" if resolved.exists() else " ⚠️ file not found"))
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))
    print(f"Wrote {output_path} ({len(rows)} outputs across {len(by_rq)} research questions)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", nargs="+", default=["cleared"],
                         help="Which register statuses to include (default: cleared only).")
    parser.add_argument("--output", default="docs/results_compendium.md",
                         help="Where to write the compiled document.")
    args = parser.parse_args()

    rows = [r for r in read_register() if r["status"] in args.status]
    if not rows:
        print(f"No outputs found with status in {args.status}. "
              "Nothing to compile yet — this is expected early in the project.")
        return

    compile_markdown(rows, REPO_ROOT / args.output)


if __name__ == "__main__":
    main()
