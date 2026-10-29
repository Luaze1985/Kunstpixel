"""H3: selve siden. Arbeidsflyt-validator, sikkerhet i koden og at den serveres riktig."""

import http.client
import re
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

from src.kunstpixel.adapters import intern_hub
from src.kunstpixel.adapters.intern_hub import PAGE_PATH, make_server
from src.kunstpixel.core.intern.agent import InternAgent

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = Path(r"C:\Users\larse\.gemini\config\skills\arbeidsflyt\scripts\verify_arbeidsflyt.py")
HTML = PAGE_PATH.read_text(encoding="utf-8")


def script_body() -> str:
    m = re.search(r"<script nonce=\"\{\{NONCE\}\}\">(.*?)</script>", HTML, re.S)
    assert m, "fant ikke script-blokken"
    return m.group(1)


# ---------- Arbeidsflyt ----------


@pytest.mark.skipif(not VALIDATOR.is_file(), reason="Arbeidsflyt-validatoren finnes ikke på denne maskinen")
def test_arbeidsflyt_validator_exits_zero():
    r = subprocess.run(["py", "-3.13", str(VALIDATOR), str(PAGE_PATH)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout


def test_page_uses_the_shared_design_file_and_af_root():
    assert '<link rel="stylesheet" href="/af.css">' in HTML
    assert '<body class="af">' in HTML
    assert (ROOT / "src/kunstpixel/adapters/datafinner/af.css").is_file()


def test_page_follows_the_approved_spec():
    assert HTML.count('data-step="') == 3  # Rolle, Spørsmål, Svar
    for tittel in ("Rolle", "Spørsmål", "Svar"):
        assert f">{tittel}</h" in HTML
    assert "af-context" in HTML  # høyre panel
    for panel in ("Rolle", "Verktøy", "Kilder", "Data", "Modell"):
        assert f'af-small-label">{panel}</span>' in HTML


def test_page_has_no_emoji_icons_or_decorative_images():
    assert not re.search("[\U0001F300-\U0001FAFF\u2600-\u27BF]", HTML)
    assert "<img" not in HTML and "<svg" not in HTML and "gradient" not in HTML


def test_all_rules_live_in_one_versioned_array():
    js = script_body()
    assert js.count("var REGLER =") == 1 and 'versjon: "1"' in js
    for rid in ("R1", "R2", "R3", "R4", "R5"):
        assert js.count(f'id: "{rid}"') == 1
    assert "ellers:" in js and "Avklar manuelt" in js


def test_decision_rules_match_the_spec_table():
    js = script_body()
    assert 'merke: "Fra interne data"' in js
    assert '["ikke_funnet", "utenfor"]' in js and '"Står ikke i dataene"' in js
    assert '["tilgang"]' in js and '"Ingen tilgang med denne rollen"' in js
    assert '["sikkerhet"]' in js and '"Kan ikke endre reglene"' in js
    assert "nettfeil: true" in js and 'tittel: "Feil"' in js


# ---------- Sikkerhet i koden ----------


@pytest.mark.parametrize(
    "forbidden",
    ["innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function", "setTimeout(\"", "localStorage", "sessionStorage", "document.cookie", "XMLHttpRequest", "postMessage", "window.open", "location.href", "location.assign"],
)
def test_page_script_avoids_dangerous_apis_and_storage(forbidden):
    assert forbidden not in script_body()


def test_page_has_no_inline_handlers_or_external_urls():
    assert not re.search(r"\son[a-z]+\s*=", HTML, re.I)
    assert not re.search(r"https?://", HTML)
    assert "javascript:" not in HTML.lower()
    assert HTML.count("<script") == 1 and HTML.count("<style") == 1


def test_only_same_origin_requests_are_made():
    urls = re.findall(r"fetch\(\s*\"([^\"]+)\"", script_body())
    assert sorted(urls) == ["/api/chat", "/api/roller"]


def test_server_text_is_only_ever_written_with_textcontent():
    js = script_body()
    assert js.count("createTextNode") == 0
    assert "textContent" in js and js.count("el(") >= 5


def test_script_is_valid_javascript():
    node = shutil.which("node")
    if not node:
        pytest.skip("node finnes ikke")
    r = subprocess.run([node, "--check", "-"], input=script_body(), capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr


# ---------- Servering ----------


def get(port, path="/"):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", path, headers={"Host": f"127.0.0.1:{port}"})
    resp = conn.getresponse()
    body = resp.read().decode("utf-8")
    h = {k.lower(): v for k, v in resp.getheaders()}
    conn.close()
    return resp.status, h, body


@pytest.fixture
def port():
    httpd = make_server(InternAgent(), port=0)
    threading.Thread(target=lambda: httpd.serve_forever(poll_interval=0.02), daemon=True).start()
    yield httpd.server_address[1]
    httpd.shutdown()
    httpd.server_close()


def test_page_is_served_with_nonce_on_script_and_style(port):
    s, h, body = get(port)
    assert s == 200 and h["content-type"].startswith("text/html")
    assert "{{NONCE}}" not in body
    nonces = set(re.findall(r'nonce="([^"]+)"', body))
    assert len(nonces) == 1
    nonce = nonces.pop()
    assert f"script-src 'nonce-{nonce}'" in h["content-security-policy"]
    assert body.count(f'nonce="{nonce}"') == 2  # ett script, én style


def test_served_page_contains_role_select_and_no_preselected_role(port):
    _, _, body = get(port)
    assert 'id="rolle-valg"' in body and "selected" not in body.split('id="rolle-valg"')[1].split("</select>")[0]


def test_served_page_matches_file_except_nonce(port):
    _, _, body = get(port)
    nonce = re.search(r'nonce="([^"]+)"', body).group(1)
    assert body.replace(nonce, "{{NONCE}}") == HTML


def test_public_chat_page_is_untouched_by_the_internal_page():
    public = (ROOT / "src/kunstpixel/adapters/chat_hub.py").read_text(encoding="utf-8")
    assert "InternAgent" not in public and "/api/roller" not in public and "intern_hub" not in public
    assert intern_hub.PAGE_PATH.parent.name == "intern"
