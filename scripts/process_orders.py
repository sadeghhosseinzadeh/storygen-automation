import os
import requests
from pathlib import Path
from storygen.generator import generate_story  # your package’s main function

# VPS host (set as env var in GitHub Actions)
VPS_HOST = os.getenv("VPS_HOST", "http://localhost:8000")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def fetch_pending_orders():
    url = f"{VPS_HOST}/orders/pending"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("orders", [])

def download_photo(sku, dest_path):
    url = f"{VPS_HOST}/photos/{sku}.jpg"
    resp = requests.get(url)
    if resp.status_code == 200:
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        return True
    else:
        print(f"⚠️ Photo not found for SKU {sku}")
        return False

def upload_story(order_id, story_path):
    url = f"{VPS_HOST}/orders/{order_id}/story"
    with open(story_path, "rb") as f:
        files = {"story": f}
        resp = requests.post(url, files=files)
    print(resp.json())

def main():
    orders = fetch_pending_orders()
    if not orders:
        print("No pending orders.")
        return

    for order in orders:
        order_id = order["order_id"]
        sku = order["sku"]
        print(f"Processing order {order_id} (SKU={sku})")

        # Step 1: Download photo
        photo_path = OUTPUT_DIR / f"{sku}.jpg"
        if not download_photo(sku, photo_path):
            continue

        # Step 2: Generate story using your package
        story_path = OUTPUT_DIR / f"{order_id}.png"
        try:
            generate_story(
                photo_path=str(photo_path),
                model_name=order["model_name"],
                sizes=order["sizes"].split(","),
                template=order["template"],
                output_path=str(story_path),
            )
            print(f"✅ Story generated: {story_path}")
        except Exception as e:
            print(f"❌ Failed to generate story for {order_id}: {e}")
            continue

        # Step 3: Upload story back to VPS
        upload_story(order_id, story_path)

if __name__ == "__main__":
    main()
