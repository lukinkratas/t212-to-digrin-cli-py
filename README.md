# T212 to Digrin CLI
Python CLI tool for fetching T212 reports via API call and transforming them to be used in Digrin portfolio tracker. Stores the reports in AWS S3.

1. Get input year_month from the CLI
2. Get first day of the input year_month selected in ad1 and first day of next year_month
3. POST request on T212 API report creation endpoint with payload containing dates from ad2.
4. GET request on T212 API list reports endpoint, loop until the created report from ad3 is finished
5. Download raw T212 CSV report from ad3.
6. Store downloaded T212 CSV from ad5 in AWS S3.
7. Decode, transform into Digrin, encode.
8. Store Digrin CSV from ad6 in AWS S3.
9. Create a presigned URL, valid for 5 min
10. Send email with URL from ad9.

## Setup

```bash
    echo "T212_API_KEY=xxx" > .env
    echo "AWS_ACCESS_KEY_ID=xxx" >> .env # or use aws configure
    echo "AWS_SECRET_ACCESS_KEY=xxx" >> .env # or use aws configure
    echo "AWS_REGION=xxx" >> .env # or use aws configure
    echo "BUCKET_NAME=xxx" >> .env
```

```bash
    uv sync
```

```bash
    uv run main.py
```

# TODO

- [ ] manage secrets via cloud

- [ ] add type hints for created variables in main()

- [ ] add logging

- [ ] archive reports in parquet ?

- [ ] add tests

- [ ] schedule via Airflow / Prefect / Github Actions / Serverless on cloud

- [x] add Ci/CD via github actions

- [x] add send mail instead of storing locally

- [x] send aws s3 temporary link and not email attachment

- [x] investigate option of asyncio + measure perf improvement -> no significant improvement

- [x] report class

- [ ] add gmail option
