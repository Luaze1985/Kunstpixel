# Kunstpixel HR Produksjonsklargjøring v1.0

Dette arkivet inneholder det komplette, kvalitetssikrede og testede datagrunnlaget for en AI-native HR-plattform for et fiktivt norsk kunstmuseum (med industri, privat sektor og kommune som referanser).

## Innhold i denne leveransen
1. `quality_report.json` – Fullstendig maskinlesbar statusrapport med alle nøkkeltall og metrikker.
2. `issues.csv` – Prioritert liste over faktiske avvik (med ID, alvorlighet, fil og tiltak).
3. `data_contract.yaml` – Standardiserte datakontrakter for kjerne- og utvidelsestabeller.
4. `rule_registry.yaml` – Samtlige 212 regler og 26 operatorer strukturert over 5 normative lag.
5. `source_registry.jsonl` – 220 kildebevis strukturert etter det autoritative kildehierarkiet.
6. `test_results.json` – Kjørelogg over beståtte tester.
7. `changes.md` – Logg over gjennomførte endringer i arbeidskopiene.
8. `blockers.md` – 5 uavklarte juridiske og ledelsesmessige forhold som krever beslutning.
9. `architecture_decision.md` – Evaluering av MintHCM, Frappe HR og Onyx med anbefalt arkitektur.
10. `README.md` – Denne filen (reproduserbar oppskrift).

## Slik gjenskapes resultatene og kjøres testene

### 1. Forutsetninger
- Python 3.10+ (anbefalt Python 3.13)
- PyYAML og pytest installert:
```powershell
py -3.13 -m pip install pyyaml pytest
```

### 2. Kjøring av den automatiserte testpakken
For å kjøre alle integritets-, regel-, kilde- og relasjonstester:
```powershell
py -3.13 -m pytest 02_deliverables/hr_produksjon_v1/tests -v
```

### 3. Verifisering av baseline mot kjerne-repoet
```powershell
py -3.13 -m pytest tests/test_db_quality.py -v
```
