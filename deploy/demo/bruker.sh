#!/usr/bin/env bash
# Legg til eller fjern en bruker som får logge inn på demoen. Kjøres på serveren, i denne mappen.
#
#   ./bruker.sh ola            # legg til (du skriver passordet to ganger, skjult)
#   ./bruker.sh --fjern ola    # fjern
#   ./bruker.sh --liste        # vis hvem som har tilgang
#
# Passordet går aldri gjennom dette skriptet: Caddy spør selv og gir bare tilbake en hash.
# Ikke send passord til noen i chat. Gi dem direkte, og be dem bytte om du kan.

set -euo pipefail
cd "$(dirname "$0")"
FIL="brukere.caddy"
touch "$FIL"

bruk() { echo "Bruk: ./bruker.sh <navn> | --fjern <navn> | --liste"; exit 1; }
gyldig() { [[ "$1" =~ ^[a-z][a-z0-9._-]{1,31}$ ]]; }
last_pa_nytt() {
  if docker compose ps --status running --services 2>/dev/null | grep -qx caddy; then
    docker compose restart caddy >/dev/null && echo "Caddy er startet på nytt, endringen gjelder nå."
  else
    echo "Caddy kjører ikke ennå. Endringen gjelder når du kjører: docker compose up -d --build"
  fi
}

case "${1:-}" in
  "") bruk ;;
  --liste) cut -d' ' -f1 "$FIL" | grep -v '^$' || echo "(ingen brukere)" ;;
  --fjern)
    navn="${2:-}"; gyldig "$navn" || bruk
    grep -q "^${navn} " "$FIL" || { echo "Fant ikke $navn."; exit 1; }
    grep -v "^${navn} " "$FIL" > "$FIL.ny" || true
    mv "$FIL.ny" "$FIL"
    echo "Fjernet $navn."
    if [ ! -s "$FIL" ]; then echo "ADVARSEL: ingen brukere igjen. Caddy starter ikke uten minst én."; fi
    last_pa_nytt
    ;;
  -*) bruk ;;
  *)
    navn="$1"; gyldig "$navn" || { echo "Ugyldig navn. Bruk små bokstaver, tall, punktum, understrek eller bindestrek (2-32 tegn)."; exit 1; }
    if grep -q "^${navn} " "$FIL"; then echo "$navn finnes allerede. Fjern først med: ./bruker.sh --fjern $navn"; exit 1; fi
    echo "Velg passord for $navn (minst 12 tegn). Du skriver det to ganger, og det vises ikke."
    hash="$(docker run --rm -it caddy:2 caddy hash-password | tr -d '\r')"
    [[ "$hash" =~ ^\$2[aby]\$ ]] || { echo "Fikk ikke en gyldig hash. Ingenting ble lagret."; exit 1; }
    printf '%s %s\n' "$navn" "$hash" >> "$FIL"
    echo "La til $navn."
    last_pa_nytt
    ;;
esac
