# E-post Handoffs — Kunstpixel Innboks- og Svararkiv

Denne mappen administrerer henvendelsesflyten for Kunstpixels e-postagenter.

## Mappestruktur
- `innkommende/`: Her legges nye, rå e-poster som tekst- eller markdown-filer (f.eks. `2026-11-14_sak_101.md`).
- `utkast/`: Her lagres de ferdig sorterte rutingene og de faglige svarutkastene fra spesialistene.

## Statusflyt for hver e-post
1. `epost_sentralbord` leser fra `innkommende/` og oppretter `<id>_ruting.yaml`.
2. Fagspesialisten (`epost_publikum`, `epost_drift`, `epost_hr` eller `epost_kurator`) genererer `<id>_svarutkast.md`.
3. `kvalitetsvokter` verifiserer faktagrunnlaget og skriver `PASS` til `<id>_gate.yaml`.
4. Menneskelig saksbehandler (Lars Erik) leser utkastet og godkjenner utsendelse.
