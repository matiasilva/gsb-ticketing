Upload all pdfs to `gsb-tickets` bucket:

```sh
gsutil cp -M *.pdf gs://gsb-tickets
```

**INFO:** this is limited by bandwidth, may take some time for large uploads.

Get env vars for local production

```bash
heroku config -a gsb-ticketing -s | grep GOOGLE >.env
```
