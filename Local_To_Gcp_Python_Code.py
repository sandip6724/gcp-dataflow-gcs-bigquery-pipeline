import os
import time
from google.cloud import storage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# === CONFIGURATION ===
WATCH_FOLDER = r'E:\GCP Project 2026'  # Your local folder path
BUCKET_NAME = 'dataflow-demo-6724'  # Your GCS bucket name
DESTINATION_FOLDER_IN_BUCKET = 'gcp_bq'  # Leave empty to upload to bucket root


class CSVHandler(FileSystemEventHandler):
    def __init__(self, gcs_client):
        self.client = gcs_client
        self.bucket = self.client.bucket(BUCKET_NAME)

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.csv'):
            time.sleep(2)  # 🔄 Wait for file to finish writing
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            destination_blob_name = file_name if not DESTINATION_FOLDER_IN_BUCKET else f"{DESTINATION_FOLDER_IN_BUCKET}/{file_name}"
            print(f"New file detected: {file_path}")
            self.upload_to_gcs(file_path, destination_blob_name)

    # Optional: Debug all file events (can be removed later)
    def on_any_event(self, event):
        print(f"Filesystem event: {event.event_type} — {event.src_path}")

    def upload_to_gcs(self, source_file, destination_blob_name):
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(source_file)
            print(f"✅ Uploaded {source_file} to gs://{BUCKET_NAME}/{destination_blob_name}")
        except Exception as e:
            print(f"❌ Failed to upload {source_file}: {e}")


def upload_existing_files(client):
    print("📦 Checking for existing .csv files in folder...")
    bucket = client.bucket(BUCKET_NAME)
    for file_name in os.listdir(WATCH_FOLDER):
        if file_name.endswith('.csv'):
            file_path = os.path.join(WATCH_FOLDER, file_name)
            destination_blob_name = file_name if not DESTINATION_FOLDER_IN_BUCKET else f"{DESTINATION_FOLDER_IN_BUCKET}/{file_name}"
            print(f"📁 Found existing file: {file_path}")
            try:
                blob = bucket.blob(destination_blob_name)
                blob.upload_from_filename(file_path)
                print(f"✅ Uploaded {file_path} to gs://{BUCKET_NAME}/{destination_blob_name}")
            except Exception as e:
                print(f"❌ Failed to upload {file_path}: {e}")


def main():
    # 🔐 Set path to service account key
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser(
        r"E:\\GCP Project 2026\\dataflow\\gen-lang-client-0155142096-472e580072c5.json"
    )

    # 🚀 Initialize GCS client
    client = storage.Client()

    # 🆙 Upload existing files before starting watcher
    upload_existing_files(client)

    # 👀 Start watching
    event_handler = CSVHandler(client)
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_FOLDER, recursive=False)
    observer.start()
    print(f"👁️ Watching folder: {WATCH_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("⛔ Stopping watcher...")
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
