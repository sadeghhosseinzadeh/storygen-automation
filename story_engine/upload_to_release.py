import argparse
import json
import os
import requests
from pathlib import Path
import mimetypes

def upload_asset(upload_url, file_path, token):
    file_path = Path(file_path)
    file_name = file_path.name

    # Normalize upload URL
    upload_url = upload_url.replace("{?name,label}", "")
    upload_url = upload_url.replace("{name}", "")
    upload_url = upload_url.replace("{label}", "")

    # Ensure ?name= is present
    if "?" not in upload_url:
        upload_url = f"{upload_url}?name={file_name}"
    else:
        if "name=" not in upload_url:
            upload_url = f"{upload_url}&name={file_name}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }

    with open(file_path, "rb") as f:
        data = f.read()

    response = requests.post(upload_url, headers=headers, data=data)

    if response.status_code not in [200, 201]:
        raise Exception(
            f"Failed to upload {file_name}: {response.status_code} {response.text}"
        )

    print(f"Uploaded asset: {file_name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload_url", required=True, help="GitHub release upload_url")
    parser.add_argument("--story_dir", required=True, help="Directory containing outputs")
    parser.add_argument("--token", required=True, help="GitHub token")
    args = parser.parse_args()

    story_dir = Path(args.story_dir)

    story_image = story_dir / "story.png"
    story_jpg = story_dir / "story.jpg"
    story_json = story_dir / "story.json"

    if not story_image.exists():
        raise FileNotFoundError("story.png not found in output directory")

    if not story_json.exists():
        raise FileNotFoundError("story.json not found in output directory")

    # Upload PNG and JSON
    upload_asset(args.upload_url, story_image, args.token)
    upload_asset(args.upload_url, story_json, args.token)

    # Upload JPG if present
    if story_jpg.exists():
        upload_asset(args.upload_url, story_jpg, args.token)
        print("Uploaded story.jpg successfully.")

    print("All story assets uploaded successfully.")


if __name__ == "__main__":
    main()
