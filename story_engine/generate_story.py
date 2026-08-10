import json
import os
import argparse
from pathlib import Path
from PIL import Image

def load_order_json(order_path):
    with open(order_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_story_image(photo_path, output_path):
    """
    For now: simply copy the input photo and save it as story.png.
    Later: replace this with your real story generation logic.
    """
    img = Image.open(photo_path)
    img.save(output_path)

def write_story_json(order, output_path):
    """
    Creates a simple JSON describing the story result.
    """
    story_data = {
        "order_id": order["order_id"],
        "status": "done",
        "story_file": "story.png"
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(story_data, f, indent=4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets_dir", required=True, help="Directory containing order.json and photos")
    parser.add_argument("--output_dir", required=True, help="Directory to write story.png and story.json")
    args = parser.parse_args()

    assets_dir = Path(args.assets_dir)
    output_dir = Path(args.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------
    # 1. Load order.json
    # -------------------------------------------------------
    order_json_path = assets_dir / "order.json"
    if not order_json_path.exists():
        raise FileNotFoundError("order.json not found in assets directory")

    order = load_order_json(order_json_path)

    # -------------------------------------------------------
    # 2. Find the first photo (photo_1.png)
    # -------------------------------------------------------
    photo_path = assets_dir / "photo_1.png"
    if not photo_path.exists():
        raise FileNotFoundError("photo_1.png not found in assets directory")

    # -------------------------------------------------------
    # 3. Generate story image (copy photo)
    # -------------------------------------------------------
    story_image_path = output_dir / "story.png"
    generate_story_image(photo_path, story_image_path)

    # -------------------------------------------------------
    # 4. Write story.json
    # -------------------------------------------------------
    story_json_path = output_dir / "story.json"
    write_story_json(order, story_json_path)

    print("Story generation complete.")

if __name__ == "__main__":
    main()
