#!/usr/bin/env python3
"""Build a run design from bio search and public GEO sample annotations."""

import argparse
import csv
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlencode
from urllib.request import urlopen


def geo_metadata(accession):
    url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?" + urlencode(
        dict(acc=accession, targ="self", form="text", view="full")
    )
    for attempt in range(3):
        try:
            with urlopen(url, timeout=60) as response:
                text = response.read().decode("utf-8")
            break
        except OSError:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
    if f"^SAMPLE = {accession}" not in text:
        raise ValueError(f"No public GEO sample record returned for {accession}")
    fields = {}
    for line in text.splitlines():
        if line.startswith("!Sample_") and " = " in line:
            key, value = line[len("!Sample_"):].split(" = ", 1)
            fields.setdefault(key, []).append(value)
    return fields


def annotations(metadata, description):
    characteristics = metadata.get("characteristics_ch1", [])
    attrs = {}
    for item in characteristics:
        key, sep, value = item.partition(":")
        if sep:
            attrs[key.strip().lower()] = value.strip()

    def pick(*keys):
        return next((attrs[key] for key in keys if attrs.get(key)), "")

    title = "; ".join(metadata.get("title", [])) or description
    condition = pick("condition", "experimental condition", "group", "sample group")
    return {
        "Title": title,
        "Condition": condition,
        "Genotype": pick("genotype", "strain", "genotype/variation"),
        "Treatment": pick("treatment", "drug", "compound"),
        "Time": pick("time", "time point", "timepoint"),
        "Replicate": pick("replicate", "biological replicate"),
        "Control": pick("control", "control status", "is control"),
        "Characteristics": json.dumps(attrs, ensure_ascii=False),
        "TreatmentProtocol": "; ".join(metadata.get("treatment_protocol_ch1", [])),
        "MetadataStatus": "GEO" if metadata else "no GEO accession; see description",
    }


def validate(path):
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"Accession", "ReadPairs"}.issubset(reader.fieldnames or []):
            raise ValueError("Expected CSV fields Accession and ReadPairs")
        rows = list(reader)
    if not rows:
        raise ValueError("Design contains no samples")
    seen = set()
    for row in rows:
        accession = row["Accession"] or ""
        if (not re.fullmatch(r"[DES]RR[0-9]+", accession)
                or not re.fullmatch(r"[1-9][0-9]*", row["ReadPairs"] or "")
                or accession in seen):
            raise ValueError(f"Invalid or duplicate run/ReadPairs: {accession}")
        seen.add(accession)
    return rows


def build(args):
    if not re.fullmatch(r"PRJ(?:NA|EB|DB)[0-9]+", args.project):
        raise ValueError("--project must be a BioProject accession (PRJNA/PRJEB/PRJDB)")
    # Parse records, rather than using head (quoted CSV fields may span lines).
    result = subprocess.run(
        ["bio", "search", "-H", "--csv", args.project],
        check=True, capture_output=True, text=True,
    )
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    reader = csv.DictReader(io.StringIO(result.stdout))
    if not {"run_accession", "sample_alias"}.issubset(reader.fieldnames or []):
        raise ValueError("bio search did not return run_accession and sample_alias")
    runs = list(reader)
    total = len(runs)
    pattern = re.compile(args.match, re.IGNORECASE)
    runs = [run for run in runs
            if pattern.search(run.get("sample_description", ""))
            and (not args.strategy or
                 run.get("library_strategy", "").lower() == args.strategy.lower())]
    print(f"Selected {len(runs)} of {total} runs before applying the limit",
          file=sys.stderr)
    if args.limit:
        runs = runs[:args.limit]
    if not runs:
        raise ValueError(f"No matching runs found for {args.project}; check filters")
    rows, cache = [], {}
    for run in runs:
        match = re.search(r"\bGSM[0-9]+\b", run.get("sample_alias", ""))
        gsm = match.group() if match else ""
        if gsm and gsm not in cache:
            print(f"Fetching {gsm}", file=sys.stderr)
            cache[gsm] = geo_metadata(gsm)
            time.sleep(0.4)
        row = {
            "Accession": run["run_accession"], "ReadPairs": args.read_pairs,
            "BioProjectId": args.project, "GEOAccession": gsm,
            "BioSample": run.get("sample_accession", ""),
            "Description": run.get("sample_description", ""),
            "LibraryLayout": run.get("library_layout", ""),
            "LibraryStrategy": run.get("library_strategy", ""),
        }
        row.update(annotations(cache.get(gsm, {}), row["Description"]))
        rows.append(row)
    # Replace only after every fetch and validation succeeds.
    output = Path(args.output)
    with tempfile.NamedTemporaryFile(mode="w", newline="", dir=output.parent,
                                     delete=False) as handle:
        temporary = Path(handle.name)
        try:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            validate(temporary)
            os.replace(temporary, output)
        finally:
            temporary.unlink(missing_ok=True)
    print(f"Wrote {len(rows)} runs to {output}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project")
    parser.add_argument("--output", default="design.csv")
    parser.add_argument("--limit", type=int, default=0,
                        help="run limit AFTER filtering; 0 means all")
    parser.add_argument("--match", default="",
                        help="case-insensitive regex on sample_description")
    parser.add_argument("--strategy", default="",
                        help="exact library strategy, e.g. ATAC-seq")
    parser.add_argument("--read-pairs", type=int, default=1200000,
                        help="maximum read pairs to download per run")
    parser.add_argument("--batch-rows", metavar="CSV")
    parser.add_argument("--batch-match", default="",
                        help="regex selecting Description for batch execution")
    args = parser.parse_args()
    try:
        if args.batch_rows:
            rows = validate(args.batch_rows)
            pattern = re.compile(args.batch_match, re.IGNORECASE)
            rows = [row for row in rows if pattern.search(row.get("Description", ""))]
            if not rows:
                raise ValueError("No design rows match --batch-match")
            for row in rows:
                print(f"{row['Accession']}\t{row['ReadPairs']}")
        else:
            if not args.project or args.limit < 0 or args.read_pairs < 1:
                parser.error("provide --project, --limit >= 0, and --read-pairs > 0")
            build(args)
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"Error: bio search failed\n{error.stderr or error}\n")
    except (OSError, ValueError, re.error) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
