"""
Branding configuration for the deliverables engine.

A ``BrandConfig`` carries the palette, font and (optional) cover assets used by
the walkthrough and presentation renderers. Everything has a sensible D55 default
so the engine renders out of the box, but each field is overridable — point it at
any client's assets/colours and the same engine produces on-brand output.

Assets are optional: if a logo/background path is missing, the renderer simply
omits it (the cover falls back to the brand gradient), so nothing hard-depends on
a particular file existing.
"""
from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Conventional asset filenames looked up by ``from_assets_dir``.
_LOGO_NAMES = ("d55-logo-white.png", "logo-white.png", "logo.png")
_BG_NAMES = ("D55_TEAMS_BACKGROUND_No_LOGO.jpg", "d55-bg.jpg", "background.jpg", "bg.jpg", "cover-bg.jpg")
_CLIENT_LOGO_NAMES = ("client-logo.png", "client-logo-white.png")


@dataclass
class BrandConfig:
    """Palette, typography and cover assets for branded deliverables."""

    # Palette
    primary: str = "#1a0a3e"   # deep navy — headings, table header, cover gradient start
    accent: str = "#5dade2"    # light blue — bullets, badges, arrows
    deep: str = "#0a4a8c"      # mid blue — cover gradient end, sub-headings
    text: str = "#23232f"      # body text

    # Typography
    font_family: str = "'Inter', 'Segoe UI', sans-serif"
    google_font_url: str = (
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap"
    )

    # Cover metadata
    eyebrow: str = ""              # small uppercase kicker above the cover title
    org_name: str = "D55 Consulting"
    date: str = ""                 # e.g. "July 2026"; DOC/deck may override

    # Cover assets (all optional)
    logo_path: Optional[Path] = None          # white logo, cover top-right
    background_path: Optional[Path] = None     # cover background image
    client_logo_path: Optional[Path] = None    # co-brand logo, cover bottom-right

    @classmethod
    def from_assets_dir(cls, assets_dir, **overrides) -> "BrandConfig":
        """Build a config by discovering conventional asset filenames in a folder.

        Any field can still be overridden via keyword args. Missing assets stay
        ``None`` (the renderer omits them gracefully).
        """
        d = Path(assets_dir)

        def _first(names):
            for n in names:
                p = d / n
                if p.exists():
                    return p
            return None

        kwargs = dict(
            logo_path=_first(_LOGO_NAMES),
            background_path=_first(_BG_NAMES),
            client_logo_path=_first(_CLIENT_LOGO_NAMES),
        )
        kwargs.update(overrides)
        return cls(**kwargs)


def b64_uri(path: Path) -> str:
    """Return a base64 ``data:`` URI for an asset so outputs stay self-contained."""
    p = Path(path)
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    data = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


def rgba(hex_color: str, alpha: float) -> str:
    """Convert ``#rrggbb`` to an ``rgba(...)`` string with the given alpha."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"
