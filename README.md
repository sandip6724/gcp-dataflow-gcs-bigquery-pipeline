# GCP Dataflow: GCS to BigQuery batch pipeline

This repository contains a batch data pipeline built with Python, Apache Beam,
Google Cloud Storage (GCS), Google Cloud Dataflow, and BigQuery.

## Current flow

```text
Local CSV folder -> GCS input prefix -> Apache Beam on Dataflow -> BigQuery
                                                        \-> invalid-row JSONL in GCS
```

The original repository files are retained. The newer implementation is added
under `src/`, with tests, configuration, and documentation alongside them.

## Repository layout

- `Local_To_Gcp_Python_Code.py` — original folder watcher/uploader (retained)
- `bq.json` — original schema file (retained)
- `udf.js` — original JavaScript transform (retained for reference)
- `employe_data.csv` — original sample input (check that it contains no real
  personal or confidential data before keeping the repository public)
- `src/upload_to_gcs.py` — one-time local CSV folder uploader using ADC
- `src/transformations.py` — CSV parsing and row validation
- `src/dataflow_pipeline.py` — Beam batch pipeline for Dataflow or DirectRunner
- `config/bigquery_schema.json` — BigQuery schema reference
- `tests/` — transformation unit tests

## Prerequisites

- Python 3.10 or 3.11 (use a Python version supported by the Beam version you install)
- A Google Cloud project with billing enabled
- A GCS bucket and a BigQuery dataset in the same or an accessible project
- Dataflow, BigQuery, and Cloud Storage APIs enabled
- IAM permissions for the user/service identity running the job

## Local setup

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Authenticate locally with Application Default Credentials:

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

Do not commit service-account JSON keys, credentials, or local environment files.
For production, use an appropriately scoped service identity and Secret Manager
or workload identity rather than a downloaded key file.

## Step 1: Upload CSV files to GCS

```bash
# Windows PowerShell example
$env:GCS_BUCKET_NAME="YOUR_BUCKET"
python -m src.upload_to_gcs --folder "E:\path\to\csv-folder" --prefix "gcp_bq"

# macOS/Linux example
export GCS_BUCKET_NAME="YOUR_BUCKET"
python -m src.upload_to_gcs --folder ./data/input --prefix gcp_bq
```

The uploader transfers each top-level `.csv` file in the folder. It does not
start Dataflow automatically.

## Step 2: Run unit tests

```bash
pytest -q
```

## Step 3: Run the pipeline locally (DirectRunner)

```bash
python -m src.dataflow_pipeline \
  --runner DirectRunner \
  --input gs://YOUR_BUCKET/gcp_bq/employe_data.csv \
  --output-table YOUR_PROJECT_ID:YOUR_DATASET.employee_data \
  --invalid-output gs://YOUR_BUCKET/errors/employee-invalid \
  --project YOUR_PROJECT_ID \
  --region us-central1 \
  --temp-location gs://YOUR_BUCKET/dataflow-temp \
  --staging-location gs://YOUR_BUCKET/dataflow-staging
```

DirectRunner is useful for local pipeline development, but a GCS/BigQuery run
still requires valid Google Cloud credentials and permissions.

## Step 4: Submit to Dataflow

Use the same command with `--runner DataflowRunner`. Ensure the Dataflow worker
service account can read the input bucket, write the output dataset, and access
the temporary/staging locations. The submitting identity also needs permission
to launch Dataflow jobs and use the worker service account.

```bash
python -m src.dataflow_pipeline \
  --runner DataflowRunner \
  --input gs://YOUR_BUCKET/gcp_bq/employe_data.csv \
  --output-table YOUR_PROJECT_ID:YOUR_DATASET.employee_data \
  --invalid-output gs://YOUR_BUCKET/errors/employee-invalid \
  --project YOUR_PROJECT_ID \
  --region us-central1 \
  --temp-location gs://YOUR_BUCKET/dataflow-temp \
  --staging-location gs://YOUR_BUCKET/dataflow-staging
```

The pipeline skips the first CSV header row, parses quoted CSV fields, validates
the expected eight columns and basic field constraints, appends valid records
to BigQuery, and writes rejected records with error messages to a GCS JSONL
output prefix. Review invalid records before retrying them.

## Data and schema notes

The expected columns are EmployeeID, FirstName, LastName, Department, Position,
Salary, JoiningDate, and Country. JoiningDate must use YYYY-MM-DD. EmployeeID
must be positive; Salary cannot be negative; FirstName and LastName are required.

Before publishing or retaining `employe_data.csv`, verify that all names,
salary figures, and other employee-like values are synthetic or that you have
permission to disclose them. Do not publish personal or confidential records.

## Current scope and limitations

- This is a batch pipeline, not a continuously streaming pipeline.
- The uploader is a separate step; it does not trigger Dataflow.
- BigQuery uses append mode. Re-running the same input can insert duplicates;
  use a deduplication/merge strategy before production scheduling.
- The original file watcher and JavaScript UDF remain untouched for backward
  compatibility/reference.
- Airflow / Cloud Composer orchestration, CI/CD deployment, schema evolution,
  data-quality metrics, and production alerting are future enhancements and
  are not claimed as implemented here.

## Troubleshooting

- `DefaultCredentialsError`: run `gcloud auth application-default login`.
- Permission errors: check GCS bucket IAM, BigQuery dataset permissions, and
  Dataflow worker service-account permissions.
- Dataflow worker startup/capacity errors: check the selected region/zone,
  quotas, and available worker capacity; retry in an approved region if needed.
- Check the invalid-row JSONL output in GCS for parse/validation failures.
