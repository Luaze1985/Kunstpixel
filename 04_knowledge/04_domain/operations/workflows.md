# Operasjonelle arbeidsflyter (Workflows)

Aura Kunstmuseum har tre kjerneflyter som er designet spesifikt for å gi praktisk verdi ved agent- og plugin-automatisering:

---

## Arbeidsflyt 1: Registrering og berikelse av verk (Verk-inntak)

```text
Rådata mottas (Tittel, kunstner, foto)
  ↓
Samlingsforvalter tildeler inventarnummer (f.eks. AURA-2026-050)
  ↓
MCP-verktøy beriker med strukturert metadata (teknikk, periode, farge/motiv-tags)
  ↓
Validering mot samlingsskjema
  ↓
Persisteres i Samlingsdatabase (SQLite / JSON)
  ↓
Status settes til «Registrert / Magasin»
```

---

## Arbeidsflyt 2: Utstillingsproduksjon og innholdsgenerering

```text
Direktør/Eier oppretter utstillingsinitiativ (f.eks. «Lys og mørke i nordisk kunst»)
  ↓
Kurator søker ut 10–15 kandidatverk via samlings-plugin
  ↓
Kurator godkjenner endelig utvalg og salplassering
  ↓
Formidler-agent genererer innholdspakke:
  - Faglig veggtekst (60–80 ord)
  - Audioguide-manus (60–90 sekunder)
  - Barne-quiz / oppdagelsesspørsmål
  - SoMe-utdrag
  ↓
Menneskelig eier / kurator gjør «one-click» review og godkjenner
  ↓
Innholdspakke lagres som klar til utstilling
```

---

## Arbeidsflyt 3: Interaktiv museumsvert (Publikumsassistent via MCP)

```text
Besøkende spør: «Hvor finner jeg verker av Theodor Kittelsen, og hva handler de om?»
  ↓
Museumsvert-agent analyserer henvendelsen
  ↓
Kaller verktøyet `search_collection(artist="Theodor Kittelsen")`
  ↓
Kaller verktøyet `get_artwork_location(artwork_id=...)`
  ↓
Syntetiserer et varmt, innbydende svar med salhenvisning og kort formidling
  ↓
Foreslår en tilpasset rute for videre opplevelse
```
