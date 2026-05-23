"""
Test Imagen 4 — confirmed available on this API key.
"""
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

print("Testing Imagen 4 Fast...")

try:
    result = client.models.generate_images(
        model="imagen-4.0-fast-generate-001",
        prompt="A clean pencil sketch storyboard frame of a person holding a vintage watch up to camera. Cinematic framing, white background, minimal lines.",
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            output_mime_type="image/jpeg",
        )
    )

    print(f"generated_images count: {len(result.generated_images)}")
    img = result.generated_images[0]
    print(f"Image object attrs: {[a for a in dir(img) if not a.startswith('_')]}")

    # Try access patterns
    if hasattr(img, 'image') and hasattr(img.image, 'image_bytes'):
        data = img.image.image_bytes
        print("Access: img.image.image_bytes ✓")
    elif hasattr(img, 'image_bytes'):
        data = img.image_bytes
        print("Access: img.image_bytes ✓")
    else:
        data = None
        print("Unknown structure — check attrs above")

    if data:
        b64 = base64.b64encode(data).decode("utf-8")
        with open("test_sketch.jpg", "wb") as f:
            f.write(data)
        print(f"\n✅ SUCCESS — {len(b64)} chars of base64. Saved as test_sketch.jpg — open it!")
    else:
        print("❌ Could not extract bytes")

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
