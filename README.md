# ETL Pipeline on Automated Scraping of Power BI Dashboards.

## Introduction.

Build a custom ETL pipeline in Python to extract monthly commodity data from various Power BI dashboards.

## Data Scrape.

[Treibstoffverbrauch in der Schweiz](https://app.powerbi.com/view?r=eyJrIjoiMTYxMGJkZDMtM2U4Zi00YmMyLWFhODUtYzgyMDc4OTdhOTkzIiwidCI6IjlkZTFhZmM4LTBlOTQtNDM0ZC1iOWU5LTdhZDMyNzdkMGZjYyIsImMiOjl9)

[INFORME SÍNTESIS MENSUAL - PRINCIPALES INDICADORES DEL MES](https://app.powerbi.com/view?r=eyJrIjoiYmFmN2RiMGItMGFhZC00M2UzLWJmYjAtMTdkNjE2M2EzOTNjIiwidCI6Ijk3NjQ0NjEyLTM3MWMtNGUzNC1hYzc1LTZlNmE1NGFmNDQyOSIsImMiOjR9)

## Export the Environment Variables inside the .env file.

```bash
=========================================================================
Paste the following credentials as environment variables.
=========================================================================

AWS_ACCESS_KEY_ID="XXXXXXXXXXXXXXXXXXXX"
AWS_REGION_NAME="ap-south-1"
AWS_SECRET_ACCESS_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
S3_BUCKET_NAME="aws-s3-bucket-name"
```

## Manual Steps to Run the Application on Windows.

```bash
# Install dependencies from the pyproject.toml to sync the project's environment.
uv sync

# Automate the Trigger.
>> uv run run_switzerland_road_diesel

>> uv run run_cammesa_etl
```

## Manual Steps to Run the Application on Docker.

- **Docker Build Command.**
  ```bash
  docker build -t <image-name>:latest .
  ```
- **Docker Run Command.**

  ```bash
  docker run -it --rm --env-file <absolute_path>/.env --cpus="0.5" -m 512m --net=host <image-name>:latest

  >> xvfb-run --auto-servernum --server-num=1 uv run run_switzerland_road_diesel

  >> xvfb-run --auto-servernum --server-num=1 uv run run_cammesa_etl
  ```

## Authors

- [Aritra Ganguly](https://in.linkedin.com/in/gangulyaritra)

## License & Copyright

[MIT License](LICENSE)
