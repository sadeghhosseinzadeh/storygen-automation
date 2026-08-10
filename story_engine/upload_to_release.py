import argparse
import json
import os
import requests
from pathlib import Path
import mimetypes

def upload_asset(upload_url, file_path, token):
    """
    Uploads a single file to a GitHub release using the release upload_url.
    """

    file_path = Path(file_path)
    file_name = file_path.name

    # GitHub requires the upload_url to end with "?name=filename"
    url = upload_url.replace("{?name,label}", f"?name={file_name}")

    mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": mime_type
            },
            data=f.read()
        )

    if response.status_code not in [200, 201]:
        raise Exception(
            f"Failed to upload {file_name}: {response.status_code} {response.text}"
        )

    print(f"Uploaded: {file_name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload_url", required=True, help="GitHub release upload_url")
    parser.add_argument("--story_dir", required=True, help="Directory containing story.png and story.json")
    parser.add_argument("--token", required=True, help="GitHub token")
    args = parser.parse_args()

    story_dir = Path(args.story_dir)

    story_image = story_dir / "story.png"
    story_json = story_dir / "story.json"

    if not story_image.exists():
        raise FileNotFoundError("story.png not found in output directory")

    if not story_json.exists():
        raise FileNotFoundError("story.json not found in output directory")

    # Upload both files
    upload_asset(args.upload_url, story_image, args.token)
    upload_asset(args.upload_url, story_json, args.token)

    print("All story assets uploaded successfully.")


if __name__ == "__main__":
    main()
