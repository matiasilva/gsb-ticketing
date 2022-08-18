#!/usr/bin/env python3

# a simple script that checks Girton student status
# matias 2021 <3

import argparse
import requests
import csv
import re

LOOKUP_ENDPOINT = "https://www.lookup.cam.ac.uk/api/v1/person/crsid/"
# ugrad
GIRTON_ID1 = "002866"
# grads
GIRTON_ID2 = "002880"
# girton staff
GIRTON_ID3 = "002836"

parser = argparse.ArgumentParser(description='verify the status of Girton students in a CSV column by email')
parser.add_argument('path',  help='file path of the CSV relative to `pwd`')
parser.add_argument('col', help='column to use', type=int)
parser.add_argument('--skip', '-s', help='skip first row as header', action='store_true', default=False)

args = parser.parse_args()
data_cols = []

girton_count = 0
invalid_count = 0

# shuffle the data we want into our array
with open(args.path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    is_first = True
    for row in reader:
        if args.skip and is_first:
            is_first = False
            continue
        data_cols.append(row[args.col])

data_cols = data_cols[:len(data_cols)-2]

for email in data_cols:
    match = re.match("([\d\w.-]+)@([\d\w.]+)", email)

    if match is None:
        print(f"👎 unable to match email {email}")

    # reject but notify non cambridge emails
    if match.group(2) != "cam.ac.uk":
        print(f"👎 non-cambridge email found: {email}")
        invalid_count += 1
        continue  

    crsid = match.group(1)
    
    # perform Lookup request
    res = requests.get(
    LOOKUP_ENDPOINT + crsid,
    params={'fetch': 'all_groups'},
    headers={'Accept': 'application/json'},
    )

    person = res.json()['result'].get('person')
    # we got a valid result, but there is no person associated with the identifier
    if person is None:
        invalid_count += 1
        continue

    # technically, the 'cancelled' field is True if you're still *in* the University for some purpose (staff)
    is_student = not person['cancelled']
    groups = person['groups']
    
    status = None
    def match_identity(group):
        if group['groupid'] == GIRTON_ID1:
            return 'girton undergrad'
        elif group['groupid'] == GIRTON_ID2:
            return 'girton postgrad'
        elif group['groupid'] == GIRTON_ID3:
            return 'girton other'
        else:
            return None
    for group in groups:
        identity = match_identity(group)
        if identity is not None:
            status = identity

    if status is None:
        print(person['groups'][0]['name'], person['groups'][1]['name'])
    else:
        print(status)

    #if is_student and is_girton:
    #    girton_count += 1
    #elif is_student:
    #    print(f"❓ non-Girton email found: {email}")

print("\n --- \n")
print(f"processed {len(data_cols)} emails")
