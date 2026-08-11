import json
import os
import argparse
import yaml
import importlib
from pathlib import Path

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

    # 1. Load order.json
    order_json_path = assets_dir / "order.json"
    order = load_order_json(order_json_path)

    # 2. Normalize template number
    template_raw = str(order.get("template", "1")).strip()
    template_name = f"template_{template_raw}"

    # 3. Load template config
    with open("story_engine/config/templates.yml") as f:
        templates_config = yaml.safe_load(f)

    template_info = templates_config.get(template_name)
    if not template_info:
        raise ValueError(f"Template {template_name} not defined in config")

    # 4. Validate required fields
    for field in template_info["required_fields"]:
        if field not in order:
            raise ValueError(f"Missing required field: {field}")

    # 5. Dynamically import the template module
    module = importlib.import_module(f"storygen.templates.{template_name}")
    generate_func = getattr(module, template_name)

    # 6. Collect arguments from order.json
    args_dict = {field: order[field] for field in template_info["required_fields"]}

    # 7. Generate story image
    story_img = generate_func(**args_dict)

    # 8. Save outputs
    story_json_path = output_dir / "story.json"
    with open(story_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "order_id": order["order_id"],
            "status": "done",
            "story_file": "story.png"
        }, f, indent=4)

    story_image_path = output_dir / "story.png"
    story_img.save(story_image_path)

    print("Story generation complete.")

if __name__ == "__main__":
    main()
