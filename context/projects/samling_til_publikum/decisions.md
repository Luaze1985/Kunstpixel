# Prosjektbeslutninger: Fra samling til publikum

## Beslutning 1: Startsett med 10–15 åpne norske og nordiske kunstverk
- **Dato:** 2026-09-14
- **Valg:** Vi benytter et startsett basert på falt i det fri-verk (public domain) av kjente kunstnere (f.eks. Theodor Kittelsen, Harriet Backer, Christian Krohg, Nikolai Astrup, Edvard Munch).
- **Hvorfor:** Ingen opphavsrettslige barrierer ved testing og undervisning; høyt gjenkjennelig innhold som gjør det lett å vurdere faglig kvalitet i formidlingen.

## Beslutning 2: Strukturert JSON / SQLite som primærlager for samlingen
- **Dato:** 2026-09-14
- **Valg:** Samlingen lagres som en ren lokal filstruktur/database (`data/collection.json` eller `data/collection.db`).
- **Hvorfor:** 0 eksterne skyavhengigheter, 100 % reproduserbart lokalt på enhver maskin for kursdeltakere.

## Beslutning 3: Human-in-the-loop for publisering
- **Dato:** 2026-09-14
- **Valg:** Automatisk genererte tekster legges i `status: draft` inntil godkjenning foreligger.
- **Hvorfor:** Sikrer etterlevelse av kvalitetspolicy og hindrer at ubekreftede tekster når publikumsflater.
