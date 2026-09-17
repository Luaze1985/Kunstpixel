"""Telegram Bridge for Aura Kunstmuseum Museumsvert.

Lar de to gründerne prate med museets agenter og teste verktøykall direkte i en Telegram-chatgruppe!
Krever kun standard `requests` (ingen tunge bot-biblioteker).

Bruk:
1. Opprett en bot hos @BotFather på Telegram (tar 1 minutt) og få en token.
2. Sett token i miljøvariabel eller .env:
   $env:TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
3. Kjør:
   py -3.13 src/telegram_bridge.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
from src.aura_museum.core.agent import MuseumsvertAgent


def get_bot_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        env_file = PROJECT_ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not token:
        print("\n❌ TELEGRAM_BOT_TOKEN mangler!")
        print("Slik setter du den:")
        print('  $env:TELEGRAM_BOT_TOKEN="din-token-her"')
        print("  eller legg den inn i en .env-fil i prosjektmappen.")
        sys.exit(1)
    return token


def main() -> None:
    token = get_bot_token()
    base_url = f"https://api.telegram.org/bot{token}"

    # Verify bot
    try:
        me_res = requests.get(f"{base_url}/getMe", timeout=10).json()
        if not me_res.get("ok"):
            print(f"❌ Ugyldig bot-token: {me_res}")
            return
        bot_name = me_res["result"]["first_name"]
        username = me_res["result"].get("username", "")
        print(f"\n✅ Tilkoblet Telegram som @{username} ({bot_name})!")
        print("🏛️ Aura Museumsvert lytter nå etter meldinger i chatten...\n")
    except Exception as e:
        print(f"❌ Nettverksfeil mot Telegram: {e}")
        return

    agent = MuseumsvertAgent()
    offset = 0

    while True:
        try:
            updates = requests.get(
                f"{base_url}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35,
            ).json()

            if not updates.get("ok"):
                time.sleep(2)
                continue

            for item in updates.get("result", []):
                offset = item["update_id"] + 1
                msg = item.get("message") or item.get("edited_message")
                if not msg or "text" not in msg:
                    continue

                chat_id = msg["chat"]["id"]
                user_name = msg.get("from", {}).get("first_name", "Gründer")
                text = msg["text"].strip()

                if text in ["/start", "/hjelp", "/help"]:
                    welcome = (
                        f"Hei {user_name}! 🏛️\n\n"
                        "Jeg er Aura Kunstmuseums AI-vert, koblet direkte til samlingsdatabasen og våre verktøy.\n\n"
                        "Prøv å spørre meg:\n"
                        "• «Hvor henger Skrik?»\n"
                        "• «Hva koster en billett for student?»\n"
                        "• «Hva anbefaler du på 30 minutter?»\n"
                        "• «Vis verk i Sal C»"
                    )
                    requests.post(
                        f"{base_url}/sendMessage",
                        json={"chat_id": chat_id, "text": welcome},
                        timeout=10,
                    )
                    continue

                print(f"💬 Mottok fra {user_name}: {text}")

                # Send typing status
                requests.post(
                    f"{base_url}/sendChatAction",
                    json={"chat_id": chat_id, "action": "typing"},
                    timeout=5,
                )

                # Process through Museumsvert
                resp = agent.handle_message(text)

                # Format response with tool tag for debugging
                tool_tag = f"\n\n🔧 Verktøy: {', '.join(resp.tools_used) or 'database'}"
                reply_text = f"{resp.text}{tool_tag}"

                requests.post(
                    f"{base_url}/sendMessage",
                    json={"chat_id": chat_id, "text": reply_text},
                    timeout=10,
                )
                print(f"👉 Svarte med verktøy: {resp.tools_used}")

        except KeyboardInterrupt:
            print("\nAvslutter Telegram-bro...")
            break
        except Exception as e:
            print(f"Feil under polling: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
