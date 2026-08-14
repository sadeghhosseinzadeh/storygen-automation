import json
import argparse
import yaml
import importlib
import inspect
from pathlib import Path
from storygen.processing import remove_background, extract_colors

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
    # Build argument pool
    args_dict = {}
    
    # Always prepare photo_1
    photo_1_path = assets_dir / order["photo_1"]
    photo_1_img = remove_background(str(photo_1_path))
    args_dict["photo_1"] = photo_1_img
    
    # Colors (only used by some templates)
    main_color, second_color = extract_colors(photo_1_img)
    args_dict["main_color"] = main_color
    args_dict["second_color"] = second_color
    
    # Add ALL fields from order.json
    for key, value in order.items():
        if key == "photo_1":
            continue
    
        if key.startswith("photo_"):
            img_path = assets_dir / value
            args_dict[key] = remove_background(str(img_path))
            continue
    
        args_dict[key] = value
    
    # --- FIELD MAPPING FOR NEW TEMPLATES ---
    if "shop_name_en" in order:
        args_dict["shop_name"] = order["shop_name_en"]
    
    if "shop_name_fa" in order:
        args_dict["shop_name"] = order["shop_name_fa"]
    
    if "logo" in order:
        args_dict["username"] = order["logo"].replace(".png", "")
    
    # Filter args based on template signature
    sig = inspect.signature(generate_func)
    final_args = {k: v for k, v in args_dict.items() if k in sig.parameters}

    
    # Filter args based on template signature
    sig = inspect.signature(generate_func)
    final_args = {k: v for k, v in args_dict.items() if k in sig.parameters}


    # 7. Filter args based on template signature
    sig = inspect.signature(generate_func)
    final_args = {k: v for k, v in args_dict.items() if k in sig.parameters}

    # 8. Generate story
    story_img = generate_func(**final_args)

    # 9. Save outputs
    with open(output_dir / "story.json", "w", encoding="utf-8") as f:
        json.dump({
            "order_id": order["order_id"],
            "status": "done",
            "story_file": "story.png"
        }, f, indent=4)

    story_img.save(output_dir / "story.png")
    print("Story generation complete.")

if __name__ == "__main__":
    main()
