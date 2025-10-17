
import time
from pathlib import Path
import requests
try:
    import replicate  # optional; fallback to stub if missing
except Exception:  # ImportError or runtime issues
    replicate = None
from ..utils.config import settings
from PIL import Image, ImageDraw

SAFE_NEGATIVE = "nsfw, nudity, gore, violence, low quality, blurry, watermark"

PROMPT_TEMPLATE = (
    "High-quality, detailed image of {subject}. "
    "Style: {style}. Lighting: {lighting}. Composition: {composition}. Lens: {lens}. "
    "Include one clear focal point."
)

class ImageGenerator:
    def __init__(self, out_dir: str = "outputs/images"):
        self.out = Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        self.client = (
            replicate.Client(api_token=settings.T2I_API_KEY)
            if (replicate is not None and settings.T2I_API_KEY)
            else None
        )

    def build_prompt(self, subject: str, style: str = "cinematic",
                     lighting: str = "soft studio", composition: str = "rule of thirds", lens: str = "50mm"):
        return PROMPT_TEMPLATE.format(subject=subject, style=style,
                                      lighting=lighting, composition=composition, lens=lens)

    def generate(self, prompt: str, negative: str = SAFE_NEGATIVE) -> str:
        ts = int(time.time())
        out_path = self.out / f"image_{ts}.png"
        try:
            if not self.client:
                raise ValueError("Replicate key missing.")
            output = self.client.run(
                settings.T2I_MODEL,
                input={"prompt": prompt, "negative_prompt": negative, "width": 768, "height": 512}
            )
            
            # Handle different output formats from Replicate
            if isinstance(output, list) and output:
                url = output[0]
                if hasattr(url, 'url'):
                    url = url.url  # FileOutput object
                elif not isinstance(url, str):
                    url = str(url)
                
                if url.startswith("http"):
                    data = requests.get(url).content
                    with open(out_path, "wb") as f:
                        f.write(data)
                    return str(out_path)
            
            raise ValueError(f"Unexpected response format: {output}")
        except Exception as e:
            print(f"Replicate API error: {e}")  # Debug: show the actual error
            # Create a better stub image with actual drawing
            img = Image.new("RGB", (768, 512), color=(240, 248, 255))  # Light blue background
            draw = ImageDraw.Draw(img)
            
            # Add a border
            draw.rectangle([(10, 10), (758, 502)], outline=(100, 100, 100), width=3)
            
            # Try to draw a simple representation based on the prompt
            prompt_lower = prompt.lower()
            
            # Center coordinates
            center_x, center_y = 384, 256
            
            if "cat" in prompt_lower:
                # Draw a simple cat
                draw.ellipse([center_x-60, center_y-40, center_x+60, center_y+40], fill=(255, 165, 0))  # Orange body
                draw.ellipse([center_x-50, center_y-50, center_x-20, center_y-20], fill=(255, 165, 0))  # Left ear
                draw.ellipse([center_x+20, center_y-50, center_x+50, center_y-20], fill=(255, 165, 0))  # Right ear
                draw.ellipse([center_x-15, center_y-15, center_x-5, center_y-5], fill=(0, 0, 0))  # Left eye
                draw.ellipse([center_x+5, center_y-15, center_x+15, center_y-5], fill=(0, 0, 0))  # Right eye
                draw.polygon([(center_x-5, center_y+5), (center_x, center_y+15), (center_x+5, center_y+5)], fill=(0, 0, 0))  # Nose
                # Whiskers
                draw.line([(center_x-60, center_y), (center_x-30, center_y)], fill=(0, 0, 0), width=2)
                draw.line([(center_x-60, center_y+5), (center_x-30, center_y+5)], fill=(0, 0, 0), width=2)
                draw.line([(center_x+30, center_y), (center_x+60, center_y)], fill=(0, 0, 0), width=2)
                draw.line([(center_x+30, center_y+5), (center_x+60, center_y+5)], fill=(0, 0, 0), width=2)
                
            elif "dog" in prompt_lower:
                # Draw a simple dog
                draw.ellipse([center_x-50, center_y-30, center_x+50, center_y+30], fill=(139, 69, 19))  # Brown body
                draw.ellipse([center_x-40, center_y-45, center_x-15, center_y-20], fill=(139, 69, 19))  # Left ear
                draw.ellipse([center_x+15, center_y-45, center_x+40, center_y-20], fill=(139, 69, 19))  # Right ear
                draw.ellipse([center_x-15, center_y-10, center_x-5, center_y], fill=(0, 0, 0))  # Left eye
                draw.ellipse([center_x+5, center_y-10, center_x+15, center_y], fill=(0, 0, 0))  # Right eye
                draw.ellipse([center_x-5, center_y+5, center_x+5, center_y+10], fill=(0, 0, 0))  # Nose
                
            elif "sunset" in prompt_lower or "sun" in prompt_lower:
                # Draw a simple sunset
                draw.ellipse([center_x-100, center_y-80, center_x+100, center_y+80], fill=(255, 165, 0))  # Sun
                draw.ellipse([center_x-80, center_y-60, center_x+80, center_y+60], fill=(255, 215, 0))  # Sun center
                
            else:
                # Generic image placeholder
                draw.ellipse([center_x-80, center_y-60, center_x+80, center_y+60], fill=(200, 200, 200))  # Gray circle
                draw.text((center_x-50, center_y-10), "IMAGE", fill=(100, 100, 100))
            
            # Add text at bottom
            draw.text((20, 480), f"Demo Image: {prompt[:50]}...", fill=(50, 50, 50))
            draw.text((20, 460), "Note: Set T2I_API_KEY in config for real images", fill=(100, 100, 100))
            
            img.save(out_path)
            return str(out_path)
