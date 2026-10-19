# ADR 010: Offentlige registre (STYRK-08 yrkeskoder og Renholdsregisteret)

**Status:** Godkjent  
**Dato:** 2026-10-19  
**Beslutningstaker:** Lars Erik Brekne Johnsen & Antigravity  

---

## Kontekst
For å unngå uformelle og vilkårlige stillingsbetegnelser og sikre seriøsitet i innleie, må museets personell og leverandører knyttes til autoritative nasjonale registre.

---

## Beslutning
1. **SSB Yrkeskatalog (STYRK-08):**  
   Alle stillinger i `hr_ansatte` kodes med offisielle STYRK-08-koder:
   - `2651.01`: Kurator / Sjefkurator (Mastergrad, kunsthistorie)
   - `2621.01`: Konservator (Mastergrad, konservering)
   - `2621.02`: Museumspedagog / Formidler (Høgskole/Universitet)
   - `5113.01`: Salvert / Museumsvert / Omviser (Videregående / internkurs)
   - `5132.01`: Kafé- og kioskmedarbeider (Videregående / IK-mat)
   - `1349.02`: Museumsdirektør / Daglig leder (Ledelse og administrasjon)
   - `1219.01`: Drifts- og eiendomssjef (Teknisk / ingeniørfag)
   - `3341.01`: Administrasjons- og HR-konsulent (HR/økonomi)
   - `5414.01`: Vekter / Vaktsjef (Nasjonal vekterutdanning)
2. **Arbeidstilsynets Renholdsregister:**  
   - Alle renholdsleverandører (f.eks. ISS Facility Services AS) sjekkes deterministisk mot registeret.
   - Statusen må være `Godkjent med ansatte` og kreve gyldige HMS-kort for alt utøvende renholdspersonell på museet.

---

## Konsekvenser
- **Offisiell rapportering:** Dataene kan rapporteres direkte til SSB og A-ordningen.
- **HMS-sikkerhet:** Museet kan ikke inngå renholdsavtaler med useriøse eller ikke-godkjente aktører.
