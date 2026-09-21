# Kontekstbygger — konseptgren v0.1

## Hva dette er

En egen konseptgren for den digitale bedriften. Den er inspirert av to kilder, men er ikke en kopi av noen av dem:

1. No Excuse-materialets styrke: strukturert intervju, tydelig skille mellom det virksomheten sier, hvordan det kan forstås, og hvilke muligheter som følger.
2. Tiago Forte-materialets styrke: kontekstarkitektur, modulær kontekst, verdier, beslutningshistorikk, context gap, context rot og menneskelig eierskap til retning og dømmekraft.

Arbeidsnavn: **Kontekstbygger**.

## Hovedidé

Kontekstbygger skal ikke primært «vurdere virksomheten». Den skal bygge et stadig bedre, kildebevisst og tidsbevisst kontekstgrunnlag som mennesker og agenter kan arbeide fra.

Grunnsløyfen er:

```text
KILDER / SAMTALE
      │
      ▼
RÅTT UTSAGN
      │
      ▼
KLASSIFISERING
fakta / beslutning / verdi /
hypotese / risiko / ukjent
      │
      ▼
FORELØPIG TOLKNING
      │
      ▼
KONTEKSTGAP / MOTSIGELSER
      │
      ▼
NESTE 1–2 SPØRSMÅL
      │
      ▼
MODULÆRE KONTEKSTFILER
      │
      ▼
AGENTARBEID / BESLUTNINGER
```

## Seks kontekstrammer

De fire første er en generell videreutvikling av organisasjonsintervju-logikken i No Excuse-materialet. De to siste legges til for agentisk arbeid og kontinuitet.

1. **Identitet og retning** — hvem vi er, hvem vi er for, hva vi ikke er, mål, verdier og ambisjon.
2. **Struktur og beslutninger** — myndighet, roller, beslutningsgrenser, måling, prioritering og arbeidsform.
3. **Mennesker og roller** — kompetanse, ansvar, avhengigheter, samhandling, styrker og gap.
4. **Omgivelser og påvirkning** — kunder, partnere, myndigheter, marked, tillit, risiko og eksterne relasjoner.
5. **Arbeid og kunnskap** — arbeidsflyter, artefakter, datakilder, verktøy, systemer, kvalitetskrav og kildebruk.
6. **Historikk og endring** — beslutningshistorikk, tidligere antakelser, endringer, læring og hvorfor dagens situasjon er som den er.

## Viktigste designvalg

- Ingen fast «60 spørsmål»-liste.
- Spørsmål velges adaptivt ut fra største kontekstgap og høyest konsekvens.
- Maks 2 spørsmål per runde.
- Det som allerede er kjent, spørres ikke om igjen.
- Rått utsagn og AI-tolkning lagres separat.
- Ingen antakelse blir til fakta uten kilde eller eksplisitt bekreftelse.
- Gamle beslutninger overskrives ikke; de får status og historikk.
- Basiskontekst holdes liten. Prosjekt-, rolle- og historikkontekst lastes ved behov.
- Eiers visjon, verdier og endelige dømmekraft kan støttes, men ikke overtas av agenten.

## Foreslått plass i senere repo

```text
workspaces/digital_bedrift/
  context_builder/
    MASTERPROMPT.md
    INTERVIEW_PROTOCOL.md
    CONTEXT_SCHEMA.yaml
  context/
    core/
    roles/
    projects/
    decisions/
    history/
    interviews/raw/
```

Dette er foreløpig en designgren. Den skal ikke kobles til ekte eksterne handlinger før policy, godkjenning og datagrenser er eksplisitt definert.
