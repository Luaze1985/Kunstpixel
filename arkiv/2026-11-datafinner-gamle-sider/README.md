# Gamle Datafinner-sider (arkivert 2026-11-06)

Disse sidene var Datafinner før den fikk «ett vindu». Nå serverer `/` skallet `src/kunstpixel/adapters/datafinner/ett-vindu.html` (oppgave 08 i `docs/specs/ett-vindu/`).

| Gammel side | Gammel adresse | Ny visning |
|---|---|---|
| `index.html` | `/`, `/index.html` | `/` (skallet) |
| `chat.html` | `/chat` | `/#flate:chat` |
| `sok.html` | `/sok.html` | `/#flate:sok` |
| `arbeidsflyt.html` | `/arbeidsflyt` | `/#flate:arbeidsflyt` |

Gamle adresser videresendes med 302 i `datafinner.py`, i `VIDERESEND`.

Vaktrommet er ikke her. Siden heter nå `vaktrom-innhold.html` og ligger igjen i `src/kunstpixel/adapters/datafinner/`, fordi skallet henter vaktrommets markup fra den. `/vaktrom` videresendes til `/#flate:vaktrom`.

Sidene serveres ikke lenger. De ligger her som kilde, slik at en kan se hvordan noe var.

- `arena.html` (flyttet 2026-11-16): egen Arena-side med Grensemodus. Arena ligger i skallet (`#arena`). Grensemodus er droppet; `/api/grense/*` består.
