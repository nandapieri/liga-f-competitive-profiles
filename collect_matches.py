import re
import json
import time
import requests

from pathlib import Path
from playwright.sync_api import sync_playwright

# =========================================================
# 1. PEGAR TODOS OS MATCH IDS + LINKS
# =========================================================

FIXTURES_URL = (
    "https://www.fotmob.com/leagues/9907/"
    "fixtures/liga-f/players?group=by-date"
)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

html = requests.get(FIXTURES_URL, headers=headers).text

match_links = sorted(
    set(
        re.findall(
            r'(/matches/[^"]+#\d{7})',
            html
        )
    )
)

matches = []

for link in match_links:
    match_id = re.search(r"#(\d{7})", link).group(1)

    matches.append({
        "match_id": match_id,
        "url": "https://www.fotmob.com" + link
    })

print(f"{len(matches)} partidas encontradas")
print(matches[:3])

# =========================================================
# 2. CONFIG
# =========================================================

RAW_DIR = Path("data/raw/matches")
RAW_DIR.mkdir(parents=True, exist_ok=True)

USER_DATA_DIR = "browser_profile"
BATCH_SIZE = 240

# =========================================================
# 3. USAR CHROME REAL COM PERFIL PERSISTENTE
# =========================================================

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        USER_DATA_DIR,
        channel="chrome",
        headless=False,
        viewport={"width": 1400, "height": 900},
        args=[
            "--disable-blink-features=AutomationControlled"
        ],
    )

    page = context.new_page()

    # abre FotMob uma vez para resolver verificação/cookies
    page.goto(
        FIXTURES_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    input("Se aparecer verificação, resolva no browser. Depois aperte ENTER aqui...")

    collected = 0

    # =====================================================
    # 4. LOOP DOS JOGOS
    # =====================================================

    for match in matches:

        match_id = match["match_id"]
        match_url = match["url"]

        output_path = RAW_DIR / f"{match_id}.json"

        if output_path.exists():
            print(f"skip {match_id}")
            continue

        print(f"\nopening {match_id}")
        print(match_url)

        try:

            # =============================================
            # ESPERAR RESPONSE REAL DA API
            # =============================================

            with page.expect_response(
                lambda response:
                f"/api/data/matchDetails?matchId={match_id}" in response.url,
                timeout=60000,
            ) as response_info:

                page.goto(
                    match_url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

            response = response_info.value

            print(response.status, response.url)

            if response.status != 200:
                try:
                    print(response.text()[:300])
                except Exception:
                    print("response was not readable")
                continue

            # =============================================
            # PEGAR JSON
            # =============================================

            data = response.json()

            # =============================================
            # SALVAR JSON
            # =============================================

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            print(f"saved {match_id}")

            collected += 1

        except Exception as e:
            print(f"failed {match_id}")
            print(e)

        time.sleep(4)

        # ================================================
        # LIMITAR BATCH
        # ================================================

        if collected >= BATCH_SIZE:
            print("\nbatch limit reached")
            break

    # =====================================================
    # 5. FECHAR BROWSER
    # =====================================================

    context.close()