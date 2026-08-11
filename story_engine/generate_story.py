import json
import os
import argparse
from pathlib import Path
from storygen.story import generate_story  # ← use your package

def load_order_json(order_path):
    with open(order_path, "r", encoding="utf-8") as f:
        return json.load(f)

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
    # 3. Normalize template number (user may send "1")
    # -------------------------------------------------------
    template_raw = str(order.get("template", "1")).strip()
    template_name = f"template_{template_raw}"

    # -------------------------------------------------------
    # 4. Generate story using storygen
    # -------------------------------------------------------
    story = generate_story(
        template_name=template_name,
        shoe_path=str(photo_path),
        model_name=order.get("model_name", "Unknown Model"),
        sizes=order.get("sizes", "").split(",")  # convert "44,45" → ["44","45"]
    )

    # -------------------------------------------------------
    # 5. Save outputs
    # -------------------------------------------------------
    story_json_path = output_dir / "story.json"
    with open(story_json_path, "w", encoding="utf-8") as f:
        json.dump({"story_text": story.text}, f, indent=4)

    story_image_path = output_dir / "story.png"
    story.image.save(story_image_path)

    print("Story generation complete.")

if __name__ == "__main__":
    main()
