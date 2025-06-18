#!/usr/bin/env python3
import json
import csv
import sys
import pathlib
import itertools


def flatten(d, parent_key="", sep="."):
    """Flatten nested dicts – {'a':{'b':1}} ➜ {'a.b':1}"""
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            yield from flatten(v, new_key, sep=sep)
        else:
            yield new_key, v


def infer_agent_from_filepath(filepath):
    # Get the parent directory name as the agent name
    path = pathlib.Path(filepath)
    parent = path.parent.name.lower()
    if parent in {"baseline_agent", "rag_agent", "cot_agent", "nli_filtered_agent"}:
        return parent
    return "unknown"


def main(infile, outfile):
    agent = infer_agent_from_filepath(str(infile))
    with open(infile, encoding="utf-8") as f:
        records = json.load(f)

    flat_rows = [dict(flatten(r)) for r in records]
    for row in flat_rows:
        row["agent"] = agent

    # Collect all unique column names
    fieldnames = list(
        dict.fromkeys(itertools.chain.from_iterable(r.keys() for r in flat_rows))
    )

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat_rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: json_to_csv.py input.json output.csv")
    main(sys.argv[1], sys.argv[2])
