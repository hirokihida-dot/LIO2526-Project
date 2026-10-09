"""E2E smoke: create_app() registry + layout stores; and real boot over HTTP."""

import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_PATHS = {"/", "/datos", "/modelos", "/lanzamiento", "/escenarios", "/exportar"}


@pytest.fixture(scope="module")
def _build_app():
    from app.app import create_app

    import dash

    app = create_app()
    return app, dash.page_registry


def _component_blob(component) -> str:
    """Flatten the component tree into a searchable string blob."""
    json_data = component.to_plotly_json()
    trozos = [
        str(json_data.get("type", "")),
        json.dumps(json_data.get("props", {}), default=str),
    ]
    children = json_data.get("props", {}).get("children")
    if children is None:
        children = []
    if not isinstance(children, list):
        children = [children]
    for hijo in children:
        if hasattr(hijo, "to_plotly_json"):
            trozos.append(_component_blob(hijo))
        elif isinstance(hijo, str):
            trozos.append(hijo)
    return " ".join(trozos)


class TestPageRegistry:
    def test_exact_path_set(self, _build_app):
        _app, registry = _build_app
        paths = {entry["path"] for entry in registry.values()}
        assert paths == EXPECTED_PATHS

    def test_layout_contains_stores_and_page_container(self, _build_app):
        app, _registry = _build_app
        blob = _component_blob(app.layout)
        assert "store-dataset" in blob
        assert "store-filtros" in blob
        # Dash 4 rewrites the imported `page_container` into this internal id.
        assert "_pages_content" in blob


def port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


class TestBootsAndServes:
    def test_http_200_with_spv_content(self):
        proc = subprocess.Popen(
            # Isolated from ROS 2 env: strip PYTHONPATH leak.
            ["env", "-u", "PYTHONPATH", f"{REPO_ROOT}/.venv/bin/python", "app/app.py"],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            deadline = time.time() + 15
            while time.time() < deadline and not port_open(8050):
                if proc.poll() is not None:
                    out, err = proc.communicate(timeout=5)
                    pytest.fail(f"App exited early: {err.decode()[-2000:]}")
                time.sleep(0.3)
            else:
                if port_open(8050) is False and proc.poll() is None:
                    pytest.fail("Server did not open port 8050 in time")
            if not port_open(8050):
                pytest.skip("Port 8050 not available (address already in use)")
            with urllib.request.urlopen("http://127.0.0.1:8050", timeout=5) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                assert resp.status == 200
                assert "SPV" in body
            # Dash internal route also responds.
            with urllib.request.urlopen(
                "http://127.0.0.1:8050/_dash-layout", timeout=5
            ) as resp:
                assert resp.status == 200
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
