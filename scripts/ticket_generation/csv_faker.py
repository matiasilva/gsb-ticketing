import argparse
import csv
import random
from pathlib import Path

from faker import Faker

fake = Faker()


parser = argparse.ArgumentParser(description="generate fake csv")
parser.add_argument("csv_file", type=Path, help="csv file path")
args = parser.parse_args()


def uuid():
    return f"GSB{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789', k=8))}"


def kind():
    if random.random() < 0.4:
        return "QJ"
    return "S"


with open(args.csv_file, 'w', newline='') as csvfile:
    fieldnames = ['name', 'uuid', 'kind']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for _ in range(1000):
        writer.writerow({'name': fake.name(), 'uuid': uuid(), 'kind': kind()})
