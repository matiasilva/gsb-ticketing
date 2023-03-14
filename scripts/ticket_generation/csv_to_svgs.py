import argparse
import base64
import csv
import io
from pathlib import Path
from string import Template

import segno

parser = argparse.ArgumentParser(description="generate svgs")
parser.add_argument("csv_file", type=Path, help="csv file path")
parser.add_argument(
    "-c",
    "--compare",
    metavar="NEW_CSV_FILE",
    type=Path,
    help="compare files and generate SVGs from entries updated in newer file",
)
args = parser.parse_args()


QUEUE_JUMP = Template(Path("QUEUE_JUMP.svg").read_text())
STANDARD = Template(Path("STANDARD.svg").read_text())

OUT_DIR = Path("svgs")
OUT_DIR.mkdir(exist_ok=True)


def csv_row_iterator():
    if not args.compare:
        with open(args.csv_file, newline="") as csvfile:
            yield from csv.DictReader(csvfile)
        return

    with open(args.csv_file, newline="") as csvfile:
        old_csv = {row["uuid"]: row for row in csv.DictReader(csvfile)}

    with open(args.compare, newline="") as csvfile:
        new_csv = {row["uuid"]: row for row in csv.DictReader(csvfile)}

    for uuid in new_csv:
        if old_csv.get(uuid, None) != new_csv[uuid]:
            yield new_csv[uuid]


for row in csv_row_iterator():
    buffer = io.BytesIO()
    qr = segno.make(row["uuid"], error="h")
    qr.save(buffer, kind="png", scale=3)
    row["qr_code"] = "data: image/png;base64, " + base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    path = OUT_DIR / (row["uuid"] + ".svg")
    if row["kind"].startswith("QJ"):
        path.write_text(QUEUE_JUMP.substitute(row))
    else:
        path.write_text(STANDARD.substitute(row))
