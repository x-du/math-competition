#!/usr/bin/env python3
"""Create a favicon from the logo: dark circle with transparent background."""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call(["pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageEnhance

# Paths
SCRIPT_DIR = Path(__file__).parent
DOCS_DIR = SCRIPT_DIR.parent / "docs"
LOGO_PATH = DOCS_DIR / "logo.png"
FAVICON_PATH = DOCS_DIR / "favicon.png"


def create_favicon():
    """Create favicon: dark circle with transparent background."""
    img = Image.open(LOGO_PATH).convert("RGBA")
    width, height = img.size

    # Crop to square from the left (graphic portion)
    size = min(width, height)
    cropped = img.crop((0, 0, size, size))

    # Make white background transparent
    data = cropped.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item
        if r > 245 and g > 245 and b > 245:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    cropped.putdata(new_data)

    # Darken the image significantly for "dark circle" look
    enhancer = ImageEnhance.Brightness(cropped)
    cropped = enhancer.enhance(0.35)
    enhancer = ImageEnhance.Contrast(cropped)
    cropped = enhancer.enhance(1.3)

    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    # Apply circular mask
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(cropped, (0, 0), mask)

    output.save(FAVICON_PATH, "PNG")
    print(f"Saved favicon to {FAVICON_PATH}")

    # Also create standard favicon sizes
    for favicon_size in [16, 32, 48, 192]:
        resized = output.resize((favicon_size, favicon_size), Image.Resampling.LANCZOS)
        out_path = DOCS_DIR / f"favicon-{favicon_size}.png"
        resized.save(out_path, "PNG")
        print(f"Saved {favicon_size}x{favicon_size} to {out_path}")

    # Create favicon.ico (multi-size for browser compatibility)
    ico_path = DOCS_DIR / "favicon.ico"
    output.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"Saved favicon.ico to {ico_path}")


if __name__ == "__main__":
    create_favicon()
