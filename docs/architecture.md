# Architecture

1. **Local ingestion:** `src/upload_to_gcs.py` uploads CSV files from a local
   folder to a configured GCS prefix using Application Default Credentials.
2. **Landing zone:** GCS stores the original CSV input.
3. **Batch processing:** Apache Beam reads the GCS object. The DataflowRunner
   executes the same Beam graph on Google Cloud Dataflow.
4. **Validation:** CSV rows are parsed with Python's CSV parser. Invalid rows
   are routed to a side output with the source row and validation error.
5. **Serving layer:** Valid rows are appended to the configured BigQuery table.

The current workflow is manually invoked in two steps (upload, then pipeline).
It does not include a trigger, scheduler, or Airflow/Cloud Composer DAG.
