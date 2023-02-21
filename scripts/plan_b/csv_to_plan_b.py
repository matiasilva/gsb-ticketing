import argparse
import csv
from datetime import datetime
from pathlib import Path

from pylatex import (
    Document,
    Head,
    LargeText,
    LineBreak,
    LongTable,
    MediumText,
    MiniPage,
    PageStyle,
    UnsafeCommand,
)
from pylatex.base_classes import Environment
from pylatex.package import Package
from pylatex.utils import NoEscape, bold

parser = argparse.ArgumentParser(description="generate ticketing plan b")
parser.add_argument("csv_file", type=Path, help="csv file path")
args = parser.parse_args()


OUT_DIR = Path("pdfs")
OUT_DIR.mkdir(exist_ok=True)

STYLE = PageStyle("firstpage")

with STYLE.create(Head("R")) as right_header:
    with right_header.create(
        MiniPage(width=NoEscape(r"0.49\textwidth"), pos="c", align="r")
    ) as r_title:
        r_title.append(LargeText(bold("Plan B")))
        r_title.append(LineBreak())
        r_title.append(
            MediumText(
                bold(datetime.now().replace(second=0, microsecond=0).isoformat())
            )
        )

with STYLE.create(Head("L")) as left_header:
    with left_header.create(
        MiniPage(width=NoEscape(r"0.49\textwidth"), pos="c", align="l")
    ) as l_title:
        l_title.append(
            LargeText(bold(NoEscape(r"Page \thepage\ of \pageref{LastPage}")))
        )


def make_doc(data: list):
    doc = Document(
        geometry_options={
            "head": "40pt",
            "margin": "0.5in",
            "bottom": "0.6in",
            "includeheadfoot": True,
        }
    )
    doc.change_document_style("firstpage")
    doc.preamble.append(STYLE)
    doc.preamble.append(NoEscape(r"\definecolor{highlight}{gray}{0.88}"))

    with doc.create(LongTable("l r", pos=["r"])) as table:
        for ticket in data:
            table.add_hline()
            uuid = NoEscape(r"\texttt{" + ticket["uuid"] + "}")
            table.add_row([ticket["name"], uuid], color=ticket["color"])

    return doc


with open(args.csv_file, newline="") as csvfile:
    queue_jump, standard = [], []
    for row in csv.DictReader(csvfile):
        if row["kind"].startswith("QJ"):
            queue_jump.append(row)
        else:
            standard.append(row)


def process(tickets: list):
    tickets.sort(key=lambda ticket: ticket["name"].lower())
    prev = None
    toggle = True
    for ticket in tickets:
        if ticket["name"].lower()[:2] != prev:
            toggle = not toggle
            prev = ticket["name"].lower()[:2]
        ticket["color"] = "highlight" if toggle else None


process(queue_jump)
process(standard)

doc = make_doc(queue_jump)
doc.generate_pdf(OUT_DIR / "queue_jump", clean_tex=False, compiler="pdflatex")
doc = make_doc(standard)
doc.generate_pdf(OUT_DIR / "standard", clean_tex=False, compiler="pdflatex")
