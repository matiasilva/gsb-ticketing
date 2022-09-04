#!/bin/bash

# empty response indicates error in parsing or API error

# TODO: check referrer to ensure nobody else can request details

PYTHONSCRIPT="""
import sys, json
res = json.load(sys.stdin)['result']
if not 'error' in res:
	person = res['person']
	clean_groups = [{k: v for k, v in groups.items() if (k == 'groupid') or (k == 'name')} for groups in person['directGroups']]
	obj = {'groups': clean_groups, 'visibleName': person['visibleName'], 'college': person['attributes'][0]['value']}
	print(json.dumps(obj))
"""

printf "Content-Type: text/plain\n\n"

saveIFS=$IFS
IFS='=&'
param=($QUERY_STRING)
IFS=$saveIFS

if [[ ${param[0]} == "user" ]]; then
	if [[ ${param[1]} =~ ^[a-z0-9]{4,7}$ ]]; then
		curl --tlsv1 --header "Accept: application/json" \
			https://www.lookup.cam.ac.uk/api/v1/person/crsid/${param[1]}?fetch=direct_groups,jdCollege | \
			python3 -c "$PYTHONSCRIPT"
	fi
fi

