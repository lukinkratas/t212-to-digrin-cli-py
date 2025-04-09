# T212 to Digrin CLI
Python CLI tool for fetching T212 reports via API call and transforming them to be used in Digrin portfolio tracker. Stores the reports in AWS S3.

```bash
echo "T212_API_KEY=xxx" >> .env
echo "AWS_ACCESS_KEY_ID=xxx" >> .env # or use aws configure
echo "AWS_SECRET_ACCESS_KEY=xxx" >> .env # or use aws configure
echo "AWS_REGION=xxx" >> .env # or use aws configure
echo "BUCKET_NAME=xxx" >> .env
```

```bash
uv run main.py
```

# TODO

- [ ] archive reports in parquet ?

- [ ] add type hints for created variables in main()

- [ ] add logging

- [ ] add tests

- [ ] investigate option of asyncio

- [ ] yield fetchReports ?

- [ ] add Ci/CD via github actions
