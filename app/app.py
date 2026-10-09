"""SPV entrypoint — Dash app factory for the sales forecasting system."""

from __future__ import annotations

import sys
from pathlib import Path

# Running as a script (`python app/app.py`) puts app/ on sys.path, not the
# repo root. Make the `app` package importable in every execution mode.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dash import Dash  # noqa: E402

from app.presentation.components.layout import root_shell  # noqa: E402

ASSETS_DIR = REPO_ROOT / "app" / "assets"
PAGES_DIR = REPO_ROOT / "app" / "presentation" / "pages"
TITULO = "SPV · Previsión de ventas"


def create_app() -> Dash:
    """Build the Dash app: multi-page registry, root shell, flask cache."""
    app = Dash(
        __name__,
        use_pages=True,
        pages_folder=str(PAGES_DIR),
        assets_folder=str(ASSETS_DIR),
        title=TITULO,
        suppress_callback_exceptions=True,
    )

    from app.adapters.caching import init_cache

    init_cache(app.server)
    app.layout = root_shell()
    return app


if __name__ == "__main__":
    create_app().run(debug=False, host="127.0.0.1", port=8050)
