# tools/destination_image.py

import os
import base64
from pathlib import Path
from typing import Dict, Any

from langchain.tools import tool
import google.generativeai as genai


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "pictures" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ ERROR: GEMINI_API_KEY is not set!")

genai.configure(api_key=API_KEY)

# ⚠️ This is probably wrong, but we'll confirm from the error.
IMAGE_MODEL_NAME = "imagen-3.0"


def _sanitize_filename(text: str) -> str:
    safe = "".join(c for c in text if c.isalnum() or c in ("_", "-")).lower()
    return safe or "image"


@tool
def destination_image(city: str, mood: str = "postcard") -> Dict[str, Any]:
    """Generate an AI image and save it."""

    print("\n================ IMAGE TOOL STARTED ================\n")
    print(f"City: {city}, Mood: {mood}")

    prompt = (
        f"High-quality travel photograph of {city}. "
        f"Realistic, wide-angle, mood: {mood}. Suitable for a travel brochure."
    )

    print(f"Prompt being sent to Gemini:\n{prompt}\n")

    try:
        # ⚠️ THIS part is where the error likely happens.
        result = genai.images.generate(
            model=IMAGE_MODEL_NAME,
            prompt=prompt,
        )
        print("Gemini API returned result:", result)

        image_obj = result.generated_images[0]
        image_bytes = base64.b64decode(image_obj.base64_data)

        filename = _sanitize_filename(f"{city}_{mood}") + ".png"
        out_path = OUTPUT_DIR / filename

        with open(out_path, "wb") as f:
            f.write(image_bytes)

        print(f"Image saved to: {out_path}\n")
        print("====================================================\n")

        return {
            "city": city,
            "image_rel_path": str(out_path.relative_to(PROJECT_ROOT)),
            "image_abs_path": str(out_path),
            "caption": f"{city} – {mood} (AI-generated)",
        }

    except Exception as e:
        print("❌ ERROR in destination_image tool:")
        print("   →", repr(e))
        print("====================================================\n")

        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "city": city,
            "prompt": prompt,
        }
