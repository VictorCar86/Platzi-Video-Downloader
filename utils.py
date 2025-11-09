import re

INVALID_CHARS = '<>:"/\\|?*'

def sanitize_filename(name: str) -> str:
    """
    Make a filename safe for Windows by:
    - Replacing spaces with underscores and trimming
    - Removing control characters
    - Replacing invalid characters: <>:"/\|?*
    - Removing trailing periods and spaces
    - Avoiding reserved device names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)

    Returns a non-empty safe string.
    """
    if not isinstance(name, str):
        name = str(name)

    # Normalize spacing
    name = name.strip().replace(" ", "_")

    # Remove control characters
    name = re.sub(r"[\x00-\x1f]", "", name)

    # Replace invalid characters
    name = re.sub(f"[{re.escape(INVALID_CHARS)}]", "_", name)

    # Remove trailing periods and spaces (not allowed on Windows)
    name = name.rstrip(" .")

    # Avoid reserved names (case-insensitive), even with extensions
    upper = name.upper()
    if re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$", upper):
        name = "_" + name

    # Ensure not empty
    return name or "unnamed"