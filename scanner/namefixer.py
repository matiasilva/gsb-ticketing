import psycopg2
import requests
from requests.adapters import HTTPAdapter, Retry

retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries=retries))

ENDPOINT = "https://mw781.user.srcf.net/lfn.cgi?user="
UPDATE_STATEMENT = "UPDATE tickets SET name = %s WHERE id = %s"

conn = psycopg2.connect(
    database="gsb23_tickets", user="matias", password="", host="localhost", port="5432"
)
cur = conn.cursor()
cur.execute("SELECT id,name,email FROM tickets WHERE name LIKE '%.%'")
result = cur.fetchall()
for ticket in result:
    ticket_id = ticket[0]
    name = ticket[1]
    crsid = ticket[2][: ticket[2].index('@')]
    if len(crsid) > 7:
        continue
    index = ticket[1].rfind('.')
    res = requests.get(ENDPOINT + crsid)
    person = res.json()
    if len(person.keys()) < 1:
        continue
    ticket_newname = person['firstName'].capitalize() + ' ' + name[index + 2 :]
    cur.execute(UPDATE_STATEMENT, (ticket_newname, ticket_id))
    conn.commit()
    print(f'changed {name} to {ticket_newname} for id {ticket_id}')

conn.commit()
cur.close()
conn.close()
