"""Upload CSV files from a local folder to a GCS prefix.

Authenticate with Application Default Credentials; do not store service
account keys in this repository.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from google.cloud import storage

def upload_csv_folder(folder: Path, bucket_name: str, prefix: str = "") -> int:
    if not folder.is_dir():
        raise NotADirectoryError(f"Input folder does not exist: {folder}")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    uploaded = 0

    for file_path in sorted(folder.glob("*")):
        if file_path.is_file() and file_path.suffix.lower() == ".csv":
            blob_name = "/".join(part for part in (prefix.strip("/"), file_path.name) if part)
            bucket.blob(blob_name).upload_from_filename(str(file_path))
            print(f"Uploaded {file_path.name} -> gs://{bucket_name}/{blob_name}")
            uploaded += 1

    print(f"Upload complete. Files uploaded: {uploaded}")
    return uploaded

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", default=os.getenv("WATCH_FOLDER", "./data/input"))
    parser.add_argument("--bucket", default=os.getenv("GCS_BUCKET_NAME"), required=False)
    parser.add_argument("--prefix", default=os.getenv("GCS_DESTINATION_FOLDER", "gcp_bq"))
    args = parser.parse_args()

    if not args.bucket:
        parser.error("Provide --bucket or set GCS_BUCKET_NAME")

    upload_csv_folder(Path(args.folder), args.bucket, args.prefix)

if __name__ == "__main__":
    main()
