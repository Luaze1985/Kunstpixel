# Datamodell og grensevern

## Separate dataområder

- `people`: `person_id`, `synthetic_flag`, `business_unit`, `role`, `employment_fraction`. Ikke bruk reelle navn, e-post, telefon eller fødselsnummer.
- `skills`: `person_id`, `skill_code`, `certificate_status`, `documented_at`, `fact_source_id`.
- `shifts`: `person_id`, `start_at`, `end_at`, `approved_status`, `source_id`.
- `observations`: `event_id`, `equipment_id`, `event_time`, `business_purpose`, `sensitivity_class`, `link_to_person_permitted`.
- `hr_cases`: `case_id`, `case_type`, `access_class`, `factual_status`, `source_id`, `case_owner_role`.
- `case_documents`: `case_id`, `document_id`, `text`, `untrusted_source`, `data_class`, `allowed_roles`.
- `decisions`: `decision_id`, `scenario_id`, `actor_role`, `candidate_action`, `approved`, `reason`, `rule_checks`, `timestamp`.
- `scenario_test_runs`: `case_id`, `model_or_rules`, `scenario_version`, `test_variant`, `authorization_leak_count`, `incorrect_sensitive_inference_count`, `human_override_required`, `pass`.

## Dataklasser

- `public_demo`: Ikke-personlige museale fakta.
- `internal_operational`: Simulerte oppgaver og bemanning.
- `hr_restricted`: Simulerte HR-saker, lønn, prestasjon og identifiserbare driftslogger.
- `special_category_simulated`: Oppdiktede data som etterligner helse/fagorganisering mv. Selv om ingen ekte personer omfattes, skal case-UI teste strengeste restriksjoner.

Klasse styrer hvilke felter *simulatoren* skal utlevere. `allowed_roles` i JSON er bare scenariodata; rettighetskontrollen må ligge i backend og må være uavhengig av klientens valg av rolle. Bruk aldri prompttekst som autorisasjonsmekanisme.

## Seks nødvendige kontroller

1. Ingen prod-data i git eller demo; syntetiske data må være selvstendig konstruert, ikke deidentifiserte virkelige HR-uttrekk.
2. Begrens felt og formål før data sendes til regelmotor eller LLM; dokumenter datalinje (source_id/fact_id).
3. Separer konfidensielle HR-saker fra bemanningsvisning og ordinær logging.
4. Test både direkte og indirekte gjenidentifisering i små grupper; ingen universell lovfestet «trygg gruppestørrelse».
5. Krev menneskelig beslutning for arbeidsrettslige tiltak. Mennesket må ha faktisk informasjon og reell mulighet til å overstyre.
6. Hold simulatoren lokalt, uten reell nettverksutgang, inntil personvern-/sikkerhetsvurderinger og tilgangsdesign foreligger.

## Særlige gråsoner

Fraværsstatus er nyttig for kapasitet, men kan brukes til å utlede helse. Maskindata er nyttig for vedlikehold, men kan bli individkontroll. Aggregater kan avsløre identitet i små team. Varslingsnotater kan inneholde navngitte eller indirekte identifiserbare tredjeparter. «Samtykke fra ansatt» er ikke et standard svar på skjev maktbalanse i arbeidsforhold. En lokal fiktiv simulering er ikke tilsvarende lovlig produksjonsbruk.
