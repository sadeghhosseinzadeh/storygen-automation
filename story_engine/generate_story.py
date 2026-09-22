import json
import argparse
import yaml
import importlib
import inspect
from pathlib import Path

def load_order_json(order_path):
    with open(order_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()

    assets_dir = Path(args.assets_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load order.json
    order = load_order_json(assets_dir / "order.json")

    # 2. Normalize template name
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

    # 5. Import template function
    module = importlib.import_module(f"storygen.templates.{template_name}")
    generate_func = getattr(module, template_name)

    # 6. Build argument pool
    args_dict = {}
    for key, value in order.items():
        if key.startswith("photo_"):
            args_dict[key] = str(assets_dir / value)  # pass path
        else:
            args_dict[key] = value

    # --- FIELD MAPPING ---
    if "shop_name_en" in order:
        args_dict["shop_name"] = order["shop_name_en"]
    if "shop_name_fa" in order:
        args_dict["shop_name"] = order["shop_name_fa"]
    
    # Logo handling
    logo_value = order.get("logo")
    if logo_value:  # only if not None or empty
        args_dict["logo"] = str(assets_dir / logo_value)
    else:
        args_dict["logo"] = None

    # 7. Filter args based on template signature
    sig = inspect.signature(generate_func)
    final_args = {k: v for k, v in args_dict.items() if k in sig.parameters}

    # 8. Generate story
    story_img = generate_func(**final_args)

    # 9. Save outputs
    # 9.1 Save PNG (High-resolution, lossless)
    story_img.save(output_dir / "story.png")

    # 9.2 Save JPG (Fast loading preview)
    try:
        rgb_img = story_img.convert("RGB")
        rgb_img.save(output_dir / "story.jpg", "JPEG", quality=95)
    except Exception as e:
        print(f"Warning: JPEG generation skipped: {e}")

    # 9.3 Save metadata JSON
    with open(output_dir / "story.json", "w", encoding="utf-8") as f:
        json.dump({
            "order_id": order["order_id"],
            "status": "done",
            "story_file": "story.png",
            "story_file_jpg": "story.jpg"
        }, f, indent=4)

    print("Story generation complete (PNG & JPG saved).")

if __name__ == "__main__":
    main()
