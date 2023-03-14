#!/bin/bash

# empty response indicates error in parsing or API error

# TODO: check referrer to ensure nobody else can request details

PYTHONSCRIPT="""
import sys, json
res = json.load(sys.stdin)['result']
if not 'error' in res:
	attrs = res['attributes']
	if len(attrs) <= 1:
		print('{}')
	else:
		obj = {'firstName': attrs[0].get('value'), 'surname': attrs[1].get('value')}
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
			https://www.lookup.cam.ac.uk/api/v1/person/crsid/${param[1]}/get-attributes?attrs=firstName,surname | \
			python3 -c "$PYTHONSCRIPT"
	fi
fi
