import hashlib


def string_to_color(text: str, min_lum=0.3, max_lum=0.8) -> str:
    """Convert a string to a color hex code, ensuring the color is within specified luminance bounds."""
    # Hash the string
    hash_digest = hashlib.sha256(text.encode()).hexdigest()

    # Get initial RGB
    r = int(hash_digest[0:2], 16)
    g = int(hash_digest[2:4], 16)
    b = int(hash_digest[4:6], 16)

    # Normalize RGB to [0, 1]
    r_norm, g_norm, b_norm = [x / 255.0 for x in (r, g, b)]

    # Compute relative luminance (ITU-R BT.709)
    luminance = 0.2126 * r_norm + 0.7152 * g_norm + 0.0722 * b_norm

    # Adjust if too dark or too bright
    def adjust_channel(c, factor):
        return min(255, max(0, int(c * factor)))

    if luminance < min_lum:
        factor = min_lum / luminance
        r, g, b = [adjust_channel(c, factor) for c in (r, g, b)]
    elif luminance > max_lum:
        factor = max_lum / luminance
        r, g, b = [adjust_channel(c, factor) for c in (r, g, b)]

    return f"#{r:02x}{g:02x}{b:02x}"
