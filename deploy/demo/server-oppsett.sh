#!/usr/bin/env bash
# Førstegangs oppsett av en ny Ubuntu 24.04-server for Datafinner-demoen.
# Kjøres ÉN gang som root, rett etter at du har logget inn første gang:
#   sudo bash server-oppsett.sh
#
# Hva det gjør (og ingenting mer):
#   1. Oppdaterer systemet og slår på automatiske sikkerhetsoppdateringer.
#   2. Installerer Docker og Docker Compose fra Ubuntus egne pakker (ingen nedlasting fra tredjepart).
#   3. Brannmur: åpner bare SSH (22), 80 og 443.
#   4. Spør før det slår av passord-innlogging (sjekker først at en SSH-nøkkel finnes, så du ikke låser deg ute).
# Skriptet er idempotent: det går bra å kjøre det flere ganger.

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then echo "Kjør som root: sudo bash $0"; exit 1; fi
. /etc/os-release
if [ "${ID:-}" != "ubuntu" ]; then
  echo "Dette skriptet er laget for Ubuntu. Du kjører: ${PRETTY_NAME:-ukjent}. Avbryter."; exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "== 1/4 Oppdaterer systemet"
apt-get update -y
apt-get upgrade -y
apt-get install -y unattended-upgrades ufw ca-certificates
dpkg-reconfigure -f noninteractive unattended-upgrades

echo "== 2/4 Installerer Docker og Compose"
apt-get install -y docker.io docker-compose-v2
systemctl enable --now docker

echo "== 3/4 Brannmur (ufw): bare SSH, 80 og 443"
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "== 4/4 SSH: slå av innlogging med passord"
NOKLER=0
for f in /root/.ssh/authorized_keys /home/*/.ssh/authorized_keys; do
  if [ -s "$f" ]; then NOKLER=1; fi
done
if [ "$NOKLER" -ne 1 ]; then
  echo "Fant ingen SSH-nøkkel på serveren. Hopper over, ellers kan du låse deg ute."
else
  read -r -p "Slå av passord-innlogging nå? Du må kunne logge inn med nøkkelen din. [j/N] " svar
  if [ "$svar" = "j" ] || [ "$svar" = "J" ]; then
    printf 'PasswordAuthentication no\nPermitRootLogin prohibit-password\n' > /etc/ssh/sshd_config.d/10-demo-herding.conf
    sshd -t
    systemctl reload ssh
    echo "Ferdig. Test i et NYTT vindu at du kommer inn med nøkkelen FØR du lukker dette."
  else
    echo "Hoppet over."
  fi
fi

echo
echo "Ferdig. Neste: hent koden og start demoen (se deploy/demo/README.md)."
echo "Tips: start serveren på nytt hvis systemet ber om det: sudo reboot"
