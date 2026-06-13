import os
import sys
import argparse
import requests
from pathlib import Path

API_URL = "http://localhost:8000"
DOCUMENTS_DIR = "documents"
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".txt", ".csv", ".md"}


def ingest_file(filepath: Path, department: str) -> dict:
    with open(filepath, "rb") as f:
        response = requests.post(
            f"{API_URL}/ingest",
            files={"file": (filepath.name, f, "application/octet-stream")},
            data={"department": department}
        )
    response.raise_for_status()
    return response.json()


def bulk_ingest(folder: str = None):
    base = Path(DOCUMENTS_DIR)

    if folder:
        departments = [folder]
    else:
        departments = [d.name for d in base.iterdir() if d.is_dir()]

    total_files = 0
    total_chunks = 0
    failed = []

    for dept in departments:
        dept_path = base / dept
        if not dept_path.exists():
            print(f"[SKIP] Folder not found: {dept_path}")
            continue

        files = [f for f in dept_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
        print(f"\n[{dept.upper()}] Found {len(files)} file(s)")

        for filepath in files:
            try:
                result = ingest_file(filepath, dept)
                print(f"  ✅ {filepath.name} — {result['chunks_created']} chunks")
                total_files += 1
                total_chunks += result["chunks_created"]
            except Exception as e:
                print(f"  ❌ {filepath.name} — FAILED: {e}")
                failed.append(filepath.name)

    print(f"\n{'='*50}")
    print(f"BULK INGEST COMPLETE")
    print(f"Files ingested : {total_files}")
    print(f"Total chunks   : {total_chunks}")
    print(f"Failed         : {len(failed)}")
    if failed:
        print(f"Failed files   : {', '.join(failed)}")
    print(f"{'='*50}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk ingest documents into Enterprise RAG")
    parser.add_argument("--folder", type=str, help="Ingest a single department folder (e.g. hr, finance)")
    args = parser.parse_args()
    bulk_ingest(folder=args.folder)
