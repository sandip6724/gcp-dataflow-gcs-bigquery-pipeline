"""Batch CSV pipeline: GCS -> Apache Beam/Dataflow -> BigQuery.

Example:
python -m src.dataflow_pipeline \
  --input gs://YOUR_BUCKET/gcp_bq/employe_data.csv \
  --output-table YOUR_PROJECT:YOUR_DATASET.employee_data \
  --invalid-output gs://YOUR_BUCKET/errors/employee-invalid \
  --project YOUR_PROJECT \
  --region us-central1 \
  --temp-location gs://YOUR_BUCKET/dataflow-temp \
  --staging-location gs://YOUR_BUCKET/dataflow-staging
"""
from __future__ import annotations

import argparse
import json
import logging

import apache_beam as beam
from apache_beam.io.gcp.bigquery import BigQueryDisposition, WriteToBigQuery
from apache_beam.options.pipeline_options import PipelineOptions

from src.transformations import parse_employee_row

SCHEMA = (
    "EmployeeID:INTEGER,FirstName:STRING,LastName:STRING,"
    "Department:STRING,Position:STRING,Salary:INTEGER,"
    "JoiningDate:DATE,Country:STRING"
)

class ParseEmployeeRow(beam.DoFn):
    """Send valid employee records to the main output and bad rows aside."""

    INVALID_TAG = "invalid"

    def process(self, line: str):
        try:
            yield parse_employee_row(line)
        except (ValueError, csv.Error) as exc:
            yield beam.pvalue.TaggedOutput(
                self.INVALID_TAG,
                json.dumps({"row": line, "error": str(exc)}),
            )

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input CSV path in GCS")
    parser.add_argument("--output-table", required=True, help="project:dataset.table")
    parser.add_argument("--invalid-output", required=True, help="GCS prefix for invalid JSONL rows")
    parser.add_argument("--project", required=True)
    parser.add_argument("--region", default="us-central1")
    parser.add_argument("--temp-location", required=True)
    parser.add_argument("--staging-location", required=True)
    parser.add_argument("--runner", default="DataflowRunner",
                        choices=["DataflowRunner", "DirectRunner"])
    return parser.parse_known_args(argv)

def run(argv=None):
    args, beam_args = parse_args(argv)
    options = PipelineOptions(
        beam_args,
        runner=args.runner,
        project=args.project,
        region=args.region,
        temp_location=args.temp_location,
        staging_location=args.staging_location,
        save_main_session=True,
    )

    with beam.Pipeline(options=options) as pipeline:
        lines = (
            pipeline
            | "Read CSV from GCS" >> beam.io.ReadFromText(
                args.input, skip_header_lines=1
            )
        )
        parsed = (
            lines
            | "Parse and validate rows" >> beam.ParDo(ParseEmployeeRow()).with_outputs(
                ParseEmployeeRow.INVALID_TAG, main="valid"
            )
        )

        (
            parsed.valid
            | "Load valid rows into BigQuery" >> WriteToBigQuery(
                table=args.output_table,
                schema=SCHEMA,
                create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=BigQueryDisposition.WRITE_APPEND,
                method=WriteToBigQuery.Method.FILE_LOADS,
                custom_gcs_temp_location=args.temp_location,
            )
        )

        (
            parsed.invalid
            | "Write invalid rows to GCS" >> beam.io.WriteToText(
                args.invalid_output,
                file_name_suffix=".jsonl",
            )
        )

if __name__ == "__main__":
    import csv  # imported here for worker-side exception handling
    logging.getLogger().setLevel(logging.INFO)
    run()
