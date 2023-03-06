import base64
import json
import os
from datetime import timedelta
from pathlib import Path

from google.cloud import storage
from google.oauth2.service_account import Credentials

# the credentials are a JSON string as a base64 environment variable - yuck
# unfortunately, google only accepts JSON, heroku works with environment
# variables and shell escape sequences are a pain, so this is my best
# compromise
cred_dict = json.loads(base64.b64decode(os.environ["GOOGLE_BASE_64_CREDS"]))
creds = Credentials.from_service_account_info(cred_dict)
client = storage.Client(credentials=creds)

# Set up your bucket and file path
file_path = "GSB.pdf"

# Get the bucket and file objects
bucket = client.bucket(os.environ["GOOGLE_BUCKET_NAME"])
blob = bucket.blob(file_path)

# Generate a signed URL with the Content-Disposition header set
url = blob.generate_signed_url(
    response_disposition="attachment;",
    version="v4",
    expiration=timedelta(hours=10),
    method="GET",
)

# Print the signed URL
print(url)
