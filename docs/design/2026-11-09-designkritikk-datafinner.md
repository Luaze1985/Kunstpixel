# Designkritikk: Datafinner – ett vindu (2026-11-09)

Siden er Kunstpixel på localhost, og første bruker er Lars, til øving. Status: fungerende prototype på vei mot finpuss.
Siden er sjekket i den innebygde nettleseren på bred skjerm (1400 × 900) med KI via Lars' egen Claude.
Kontrast og skriftstørrelser er målt på siden.

**Lars' mål etter kritikken:** *«deilige, smoothe rapporter, og LLM som finner data, krysskobler og lager sammenhenger»* (se DECISIONS punkt 15).

## Helhetsinntrykk
Siden virker ryddig og pålitelig. Fasit-kolonnen er det sterkeste grepet: verktøy, kilde og regel står synlig ved hvert svar.
Den største muligheten er å kutte støy. Det meste vises to ganger, og menyen er lang, så det motsier «minst mulig støy» (DECISIONS punkt 11).

## Brukervennlighet
| Funn | Alvor | Anbefaling |
|---|---|---|
| Rapportene står to steder: i venstremenyen og som kort i midten. | 🟡 Moderat | Vis rapportene i midten og la menyen bare navigere: rolle, Spør KI og grupper som kan foldes inn. |
| Venstremenyen er lang (KI, rapporter, Arena med casetall, Flater). Arena og Flater konkurrerer med de daglige rapportene. | 🟡 Moderat | Fold «Arena» og «Flater» sammen som standard, eller flytt dem bak «Mer». |
| I rapporten tar skjemaet (År, Kvartal) halve skjermen, og svaret havner under skjermkanten. | 🟡 Moderat | Legg feltene på én linje med smale felt, og la nøkkeltallene komme først. |
| Nøkkeltallene står både som store tall og i Fakta-tabellen rett under. | 🟢 Liten | Fjern radene fra tabellen som allerede vises som nøkkeltall. |
| Rollevalget kuttes («HR og bemannin…»). | 🟢 Liten | Gjør menyen bredere, eller vis rollen som tekst med en «Bytt»-lenke. |
| Fasit står tom («Ingen ennå») på rollesidene og tar en hel kolonne. | 🟢 Liten | Vis en kort forklaring der til et svar er valgt, eller skjul kolonnen på sider uten svar. |
| Chat: eksempelspørsmålene blir stående etter første svar. | 🟢 Liten | Skjul dem når samtalen har startet. |
| Mobil: «Gå til»-velgeren er tom på forsiden. | 🟢 Liten | Velg «Hvem er du?» som standard i velgeren. |

## Visuelt hierarki
- **Det øyet ser først** er den blå «Øvingsdata»-boksen. Den står øverst på hver side og tar blikket fra overskriften.
- **Leseretningen** er overskrift → kort → Fasit. Den virker godt på rollesidene. I rapportene bryter skjemaet flyten før svaret.
- **Vekting:** nøkkeltallene er riktig fremhevet. «Spør KI» er bare én tekstlenke under en liten «KI»-overskrift, så den egne inngangen fra punkt 12 synes knapt.
- **Små etiketter:** «Rapporter for» over overskriften og «Rapport Utkast» under knappen er så små og tette at de blir lette å overse.

## Konsistens
| Element | Problem | Anbefaling |
|---|---|---|
| Regel i Fasit | Viser rå feltnavn, for eksempel `R-FRAV-01: egen_prosent <= 7`. | Bruk den samme etikettfunksjonen som tabellene: «Egenmeldt andel ≤ 7 %». |
| Verktøy i Fasit | Viser rå JSON. | Greit for øving, men vis gjerne `get_absence_report(år 2025, kvartal 2)`. |
| Skriftstørrelser | Sju ulike størrelser mellom 11,2 og 13,8 px i små etiketter. | Samle dem i to trinn, for eksempel 12 og 14 px. |
| Merker | «Utkast», «AI-forslag» og «Bør verifiseres» har samme gule farge. | Bruk egne farger for status og kilde. |

## Tilgjengelighet
- **Fargekontrast:** alt jeg målte består WCAG AA. Laveste verdi er 5,35:1 på de gule merkene, og brødtekst og tabeller ligger på 8–14,5:1.
- **Klikkflater:** avkrysningsboksene er 19 × 19 px, men hele etiketten er klikkbar. Lenken «Se alle tabellene» er bare 19 px høy, under anbefalt minimum på 24 px.
- **Lesbarhet:** brødtekst og tabeller er 14–16 px. Etiketter, menystatus og Fasit-titler er 11,2–11,7 px, i nedre grense.

## Det som fungerer
- **Fasit-kolonnen** gjør «tall fra databasen, KI formulerer» synlig ved hvert svar.
- **Nøkkeltallene** har tydelige store tall, og «Utkast» blir «Bekreftet» etter kontrollpunkter.
- **Rolle først** («Hvem er du?») gir relevante rapporter uten søk.
- **Rolig fargebruk** med god kontrast og ingen visuell støy.

## Viktigste tiltak
1. **Fjern dobbeltvisningen av rapporter i menyen.** Det kutter mest støy med minst arbeid.
2. **Gjør «Spør KI» til en tydelig knapp** øverst i menyen, ikke en tekstlenke.
3. **Komprimer rapportskjemaet** til én linje og vis nøkkeltallene først, så svaret står på første skjerm.
