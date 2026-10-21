#!/usr/bin/env python3
"""Execute R examples, build the course, and package reproducible downloads."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BUILD = ROOT / "_build"


def run(command, **kwargs):
    print("Running", " ".join(map(str, command)), flush=True)
    return subprocess.run(command, check=True, text=True, **kwargs)


def execute_labs():
    rscript = os.environ.get("RSCRIPT") or shutil.which("Rscript")
    if not rscript:
        raise SystemExit("Rscript is required. Install R or set RSCRIPT to its executable.")
    generated = DOCS / "_generated"
    labcopy = DOCS / "_static/labs"
    outputcopy = DOCS / "_static/lab-outputs"
    figures = DOCS / "_static/figures"
    for folder in (generated, labcopy, outputcopy, figures):
        folder.mkdir(parents=True, exist_ok=True)
    version = run([rscript, "--vanilla", "-e", 'cat(R.version.string)'], capture_output=True).stdout.strip()
    packages = run([rscript, "--vanilla", "-e", 'for (p in c("clusterpval", "KmeansInference")) if (requireNamespace(p, quietly=TRUE)) cat(p, as.character(packageVersion(p)), "\\n")'], capture_output=True).stdout.strip()
    records = []
    scripts = sorted((ROOT / "labs").glob("[0-9][0-9]-*.R"))
    if len(scripts) != 14:
        raise SystemExit(f"Expected 14 chapter labs, found {len(scripts)}.")
    for script in scripts:
        env = os.environ.copy()
        env["COURSE_FIGURE_DIR"] = str(figures)
        # Each script starts in a clean working directory and fresh R process.
        with tempfile.TemporaryDirectory(prefix="tsl-lab-") as tmp:
            result = run([rscript, "--vanilla", str(script)], cwd=tmp, env=env,
                         capture_output=True, timeout=240)
        output = result.stdout.strip()
        if result.stderr.strip():
            output += "\n\nDiagnostics:\n" + result.stderr.strip()
        if not output:
            raise SystemExit(f"No evidence was printed by {script.name}.")
        output_bytes = (output + "\n").encode("utf-8")
        (outputcopy / f"{script.stem}.txt").write_bytes(output_bytes)
        shutil.copy2(script, labcopy / script.name)
        block = "::::{container} cell_output\n\n```text\n" + output + "\n```\n"
        figure = figures / f"{script.stem}.png"
        if figure.exists():
            block += f"\n```{{image}} ../_static/figures/{figure.name}\n:alt: Experiment results for {script.stem[3:].replace('-', ' ')}; numerical results are printed above.\n:width: 100%\n```\n"
        block += "\n::::\n"
        (generated / f"{script.stem}-output.md").write_text(block)
        records.append({"script": script.name, "sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
                        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
                        "status": "executed", "figure": figure.name if figure.exists() else None})
    manifest = {"course": "Topics of Statistical Learning", "executed_at_utc": datetime.now(timezone.utc).isoformat(),
                "r_version": version, "optional_packages": packages.splitlines(), "labs": records}
    (outputcopy / "execution-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def package_labs():
    downloads = DOCS / "_static/downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    with ZipFile(downloads / "statistical-learning-labs.zip", "w", ZIP_DEFLATED) as bundle:
        for folder in (DOCS / "_static/labs", DOCS / "_static/lab-outputs", DOCS / "_static/figures"):
            for path in sorted(folder.glob("*")):
                if path.is_file():
                    bundle.write(path, f"{folder.name}/{path.name}")
        bundle.writestr("README.txt", "Topics of Statistical Learning\n\nRun a lab in a fresh R session, for example:\nRscript --vanilla labs/03-pu-learning.R\n\nRequired calculations use base R. Optional clusterpval and KmeansInference calculations run when installed. See the course workflow and chapter notes for assumptions and installation links.\n\nlab-outputs contains executed stdout and an execution manifest. The code is the source of the results; recorded outputs are reference evidence, not a substitute for execution.\n\nCourse: https://chikuang.github.io/teaching/statistical-learning/\n")


def build_pdf():
    run([sys.executable, "-m", "sphinx", "-b", "latex", "-E", "-W", "--keep-going", str(DOCS), str(BUILD / "latex")])
    run(["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "Topics-of-Statistical-Learning.tex"], cwd=BUILD / "latex", stdout=open(BUILD / "latex-build.log", "w"), stderr=subprocess.STDOUT)
    pdf = BUILD / "latex/Topics-of-Statistical-Learning.pdf"
    (BUILD / "html").mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf, BUILD / "html" / pdf.name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("html", "pdf", "all"), default="all")
    parser.add_argument("--skip-labs", action="store_true", help="Reuse already executed outputs for editorial rebuilds.")
    args = parser.parse_args()
    if not args.skip_labs:
        execute_labs()
    elif not (DOCS / "_static/lab-outputs/execution-manifest.json").exists():
        raise SystemExit("No recorded execution exists. Build without --skip-labs first.")
    package_labs()
    if args.format in ("html", "all"):
        run([sys.executable, "-m", "sphinx", "-b", "html", "-E", "-d", str(BUILD / "doctrees/html"), "-W", "--keep-going", str(DOCS), str(BUILD / "html")])
    if args.format in ("pdf", "all"):
        build_pdf()
    print("Course build completed.")


if __name__ == "__main__":
    main()
