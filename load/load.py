import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContentSettings

def upload_json_to_blob(file_path: str, blob_key: str, container_name: str = "media") -> str:
    """
    Upload a local .json file to Azure Blob Storage.

    Args:
        file_path: Local path to the .json file (e.g., "./data/sample.json").
        blob_key: Destination blob key/name inside the container (e.g., "datasets/2025/sample.json").
        container_name: Target container name (defaults to "media").

    Returns:
        The blob URL (publicly accessible only if the container ACL allows it).
    """
    # Load environment variables from .env (AZURE_STORAGE_ACCOUNT_NAME, AZURE_STORAGE_KEY)
    load_dotenv()

    # Default account name to "chiwinnersmedia" if not provided
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "chiwinnersmedia")
    account_key = os.getenv("AZURE_STORAGE_KEY")
    if not account_key:
        # Fail fast if the account key is missing
        raise RuntimeError(
            "Missing AZURE_STORAGE_KEY in your .env. "
            "Add AZURE_STORAGE_KEY=... and try again."
        )

    # Build the account URL and initialize the BlobServiceClient using the account key
    account_url = f"https://{account_name}.blob.core.windows.net"
    service = BlobServiceClient(account_url=account_url, credential=account_key)

    # Ensure the container exists; ignore the error if it already exists
    try:
        service.create_container(container_name)
    except ResourceExistsError:
        pass

    # Validate the input file
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p.resolve()}")
    if p.suffix.lower() != ".json":
        raise ValueError("This uploader expects a .json file. Please check the extension.")

    # Get a client for the target blob (container + blob key)
    blob = service.get_blob_client(container=container_name, blob=blob_key)

    # Upload the file stream with the correct content type and allow overwriting
    with p.open("rb") as f:
        blob.upload_blob(
            f,
            overwrite=True,
            content_settings=ContentSettings(content_type="application/json")
        )

    # Return the full URL to the uploaded blob (visibility depends on container access level)
    return f"{account_url}/{container_name}/{blob_key}"

def main():
    # CLI: parse required file path and destination key; container is optional
    parser = argparse.ArgumentParser(description="Upload a .json file to Azure Blob Storage.")
    parser.add_argument("--file", required=True, help="Local path to the .json file")
    parser.add_argument("--blob-key", required=True, help="Destination key in the container (e.g., 'folder/file.json')")
    parser.add_argument("--container", default="media", help="Target container name (default: media)")
    args = parser.parse_args()

    # Perform the upload and print the resulting URL
    url = upload_json_to_blob(args.file, args.blob_key, args.container)
    print("Upload completed successfully.")
    print(f"Blob URL: {url}")

if __name__ == "__main__":
    main()
