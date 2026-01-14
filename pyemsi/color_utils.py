"""Color conversion utilities for different color formats.

Supports conversions between:
- Hex strings: "#FF5733" or "FF5733"
- RGB tuples: (255, 87, 51) or normalized (1.0, 0.34, 0.2)
- RGBA tuples: (255, 87, 51, 255) or normalized (1.0, 0.34, 0.2, 1.0)
- Named colors: "red", "blue", etc. (matplotlib color names)
- PyVista Color objects
- Matplotlib colors
- QColor objects (PySide6/PyQt)
"""

from typing import Union, Tuple, Literal, Optional
import re


ColorType = Union[
    str, Tuple[int, int, int], Tuple[int, int, int, int], Tuple[float, float, float], Tuple[float, float, float, float]
]


def normalize_rgb(rgb: Tuple[Union[int, float], ...]) -> Tuple[float, float, float]:
    """Normalize RGB values to 0-1 range.

    Args:
        rgb: RGB tuple with values either in 0-255 or 0-1 range

    Returns:
        Normalized RGB tuple with values in 0-1 range
    """
    # Check if values are already normalized (all <= 1.0)
    if all(0 <= v <= 1.0 for v in rgb[:3]):
        return tuple(rgb[:3])
    # Convert from 0-255 to 0-1
    return tuple(v / 255.0 for v in rgb[:3])


def denormalize_rgb(rgb: Tuple[float, float, float]) -> Tuple[int, int, int]:
    """Convert normalized RGB (0-1) to 0-255 range.

    Args:
        rgb: Normalized RGB tuple with values in 0-1 range

    Returns:
        RGB tuple with values in 0-255 range
    """
    return tuple(int(round(v * 255)) for v in rgb)


def hex_to_rgb(hex_color: str, normalized: bool = False) -> Union[Tuple[int, int, int], Tuple[float, float, float]]:
    """Convert hex color string to RGB tuple.

    Args:
        hex_color: Hex color string ("#FF5733" or "FF5733")
        normalized: If True, return values in 0-1 range, else 0-255

    Returns:
        RGB tuple

    Raises:
        ValueError: If hex_color format is invalid
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip("#")

    # Validate format
    if not re.match(r"^[0-9A-Fa-f]{6}$", hex_color):
        raise ValueError(f"Invalid hex color format: {hex_color}")

    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    if normalized:
        return (r / 255.0, g / 255.0, b / 255.0)
    return (r, g, b)


def rgb_to_hex(rgb: Tuple[Union[int, float], ...]) -> str:
    """Convert RGB tuple to hex color string.

    Args:
        rgb: RGB tuple with values in 0-255 or 0-1 range

    Returns:
        Hex color string with '#' prefix
    """
    # Normalize if needed
    if all(isinstance(v, float) and v <= 1.0 for v in rgb[:3]):
        rgb = denormalize_rgb(rgb[:3])

    return f"#{int(rgb[0]):02X}{int(rgb[1]):02X}{int(rgb[2]):02X}"


def parse_color(color: ColorType) -> Tuple[float, float, float, float]:
    """Parse any color format to normalized RGBA tuple.

    Args:
        color: Color in any supported format:
            - Hex string: "#FF5733" or "FF5733"
            - RGB tuple: (255, 87, 51) or (1.0, 0.34, 0.2)
            - RGBA tuple: (255, 87, 51, 255) or (1.0, 0.34, 0.2, 1.0)
            - Named color: "red", "blue", etc.

    Returns:
        Normalized RGBA tuple (r, g, b, a) with values in 0-1 range

    Raises:
        ValueError: If color format is not recognized
    """
    # Handle string (hex or named color)
    if isinstance(color, str):
        # Try hex format first
        if color.startswith("#") or re.match(r"^[0-9A-Fa-f]{6}$", color):
            rgb = hex_to_rgb(color, normalized=True)
            return (*rgb, 1.0)

        # Try named color (requires matplotlib)
        try:
            import matplotlib.colors as mcolors

            if color.lower() in mcolors.CSS4_COLORS:
                hex_color = mcolors.CSS4_COLORS[color.lower()]
                rgb = hex_to_rgb(hex_color, normalized=True)
                return (*rgb, 1.0)
        except ImportError:
            pass

        raise ValueError(f"Unrecognized color format: {color}")

    # Handle tuple
    if isinstance(color, (tuple, list)):
        if len(color) == 3:
            # RGB tuple
            rgb = normalize_rgb(color)
            return (*rgb, 1.0)
        elif len(color) == 4:
            # RGBA tuple
            rgb = normalize_rgb(color[:3])
            # Normalize alpha if needed
            alpha = color[3]
            if alpha > 1.0:
                alpha = alpha / 255.0
            return (*rgb, alpha)
        else:
            raise ValueError(f"Color tuple must have 3 or 4 elements, got {len(color)}")

    raise ValueError(f"Unsupported color type: {type(color)}")


def convert_color(
    color: ColorType,
    output_format: Literal[
        "hex", "rgb", "rgba", "rgb_normalized", "rgba_normalized", "pyvista", "matplotlib", "qcolor"
    ] = "hex",
    alpha: Optional[float] = None,
) -> Union[str, Tuple, object]:
    """Convert color to specified output format.

    Args:
        color: Input color in any supported format
        output_format: Desired output format:
            - "hex": Hex string "#RRGGBB"
            - "rgb": RGB tuple (0-255 range)
            - "rgba": RGBA tuple (0-255 range)
            - "rgb_normalized": RGB tuple (0-1 range)
            - "rgba_normalized": RGBA tuple (0-1 range)
            - "pyvista": pyvista.Color object
            - "matplotlib": matplotlib color tuple
            - "qcolor": PySide6.QtGui.QColor object
        alpha: Optional alpha value to override (0-1 range)

    Returns:
        Color in requested format

    Raises:
        ValueError: If color format is invalid
        ImportError: If required library is not available

    Examples:
        >>> convert_color("#FF5733", "rgb")
        (255, 87, 51)

        >>> convert_color((255, 87, 51), "hex")
        '#FF5733'

        >>> convert_color("red", "rgb_normalized")
        (1.0, 0.0, 0.0)

        >>> convert_color((1.0, 0.5, 0.0), "rgba", alpha=0.5)
        (255, 128, 0, 128)
    """
    # Parse input to normalized RGBA
    r, g, b, a = parse_color(color)

    # Override alpha if specified
    if alpha is not None:
        a = float(alpha)

    # Convert to requested format
    if output_format == "hex":
        return rgb_to_hex((r, g, b))

    elif output_format == "rgb":
        return denormalize_rgb((r, g, b))

    elif output_format == "rgba":
        rgb_255 = denormalize_rgb((r, g, b))
        return (*rgb_255, int(round(a * 255)))

    elif output_format == "rgb_normalized":
        return (r, g, b)

    elif output_format == "rgba_normalized":
        return (r, g, b, a)

    elif output_format == "pyvista":
        try:
            import pyvista as pv

            return pv.Color((r, g, b), opacity=a)
        except ImportError:
            raise ImportError("PyVista is required for 'pyvista' output format")

    elif output_format == "matplotlib":
        # Matplotlib uses normalized RGBA
        return (r, g, b, a)

    elif output_format == "qcolor":
        try:
            from PySide6.QtGui import QColor

            rgb_255 = denormalize_rgb((r, g, b))
            return QColor(rgb_255[0], rgb_255[1], rgb_255[2], int(round(a * 255)))
        except ImportError:
            try:
                from PyQt6.QtGui import QColor

                rgb_255 = denormalize_rgb((r, g, b))
                return QColor(rgb_255[0], rgb_255[1], rgb_255[2], int(round(a * 255)))
            except ImportError:
                raise ImportError("PySide6 or PyQt6 is required for 'qcolor' output format")

    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def color_from_pyvista(pv_color) -> Tuple[float, float, float, float]:
    """Extract normalized RGBA from PyVista Color object.

    Args:
        pv_color: pyvista.Color object

    Returns:
        Normalized RGBA tuple
    """
    try:
        import pyvista as pv

        if not isinstance(pv_color, pv.Color):
            raise ValueError("Input must be a pyvista.Color object")

        # PyVista Color has float_rgb property and opacity
        rgb = pv_color.float_rgb
        opacity = pv_color.opacity if hasattr(pv_color, "opacity") else 1.0
        return (*rgb, opacity)
    except ImportError:
        raise ImportError("PyVista is required to parse PyVista Color objects")


def color_from_qcolor(qcolor) -> Tuple[float, float, float, float]:
    """Extract normalized RGBA from QColor object.

    Args:
        qcolor: PySide6.QtGui.QColor or PyQt6.QtGui.QColor object

    Returns:
        Normalized RGBA tuple
    """
    try:
        from PySide6.QtGui import QColor

        qcolor_class = QColor
    except ImportError:
        try:
            from PyQt6.QtGui import QColor

            qcolor_class = QColor
        except ImportError:
            raise ImportError("PySide6 or PyQt6 is required to parse QColor objects")

    if not isinstance(qcolor, qcolor_class):
        raise ValueError("Input must be a QColor object")

    return (qcolor.redF(), qcolor.greenF(), qcolor.blueF(), qcolor.alphaF())


# Convenience functions for common conversions
def to_hex(color: ColorType) -> str:
    """Convert any color to hex string."""
    return convert_color(color, "hex")


def to_rgb(color: ColorType, normalized: bool = False) -> Tuple:
    """Convert any color to RGB tuple."""
    if normalized:
        return convert_color(color, "rgb_normalized")
    return convert_color(color, "rgb")


def to_rgba(color: ColorType, normalized: bool = False, alpha: Optional[float] = None) -> Tuple:
    """Convert any color to RGBA tuple."""
    if normalized:
        return convert_color(color, "rgba_normalized", alpha=alpha)
    return convert_color(color, "rgba", alpha=alpha)


def to_pyvista(color: ColorType, alpha: Optional[float] = None):
    """Convert any color to PyVista Color object."""
    return convert_color(color, "pyvista", alpha=alpha)


def to_qcolor(color: ColorType, alpha: Optional[float] = None):
    """Convert any color to QColor object."""
    return convert_color(color, "qcolor", alpha=alpha)


def to_matplotlib(color: ColorType, alpha: Optional[float] = None) -> Tuple[float, float, float, float]:
    """Convert any color to matplotlib color (normalized RGBA)."""
    return convert_color(color, "matplotlib", alpha=alpha)
