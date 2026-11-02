# Research-rapport: Realisme i museumstall og besøksdata (2010–2026)

**Dato:** 2026-10-18  
**Forfatter:** Antigravity (Research Agent)  
**Primærkilder:** 
- Statistisk sentralbyrå (SSB), Tabell 12362: Museer og samlinger (2010–2024)
- Kulturdirektoratet: *Kulturens tilstand 2024* og årlige museumsregnskaper
- Kunstpixels eget utstillingsarkiv (`05_data/arkiv_utstillinger_2010_2026.csv`)

---

## 1. Hovedfunn fra offisielle tall (SSB)

Norske museer hadde følgende reelle utvikling fra 2010 til 2024:

1. **Stabil periode (2010–2019):**  
   Nasjonalt lå besøket stabilt mellom 10,4 og 11,3 millioner per år. For et mellomstort kunstmuseum tilsvarer dette et stabilt årsvolum på ca. **125 000 – 145 000 besøkende**.
2. **Koronakrakket (2020–2021):**  
   I 2020 falt nasjonalt museumsbesøk fra 10,4 mill. til **5,1 mill. (et fall på over 50 %)**. For kunstmuseer i byer var fallet enda større (ofte 60–70 %) grunnet nedstengte perioder og null utenlandsturisme. I 2021 var det en moderat oppgang til 6,4 mill.
3. **Post-pandemisk rekyl (2022–2024):**  
   I 2022 spratt besøket tilbake til 10,3 mill., og nådde i 2024 over **11,5 mill. besøk**, hvorav ca. 6,5 millioner var betalende gjester.

---

## 2. Reell billettprisutvikling (2010–2026)

Kulturdirektoratets rapporter viser at billettprisene har steget betydelig mer enn generell konsumprisindeks (KPI) i perioden:

| Periode | Voksenbillett (Normalt nivå) | Student / Honnør | Barn under 16 |
| :--- | :--- | :--- | :--- |
| **2010–2014** | 60 – 75 kr | 40 – 50 kr | Gratis |
| **2015–2019** | 80 – 100 kr | 60 – 70 kr | Gratis |
| **2020–2022** | 100 – 110 kr | 70 – 80 kr | Gratis |
| **2023–2026** | 120 – 150 kr | 80 – 100 kr | Gratis |

---

## 3. Konklusjon og kalibreringskrav for Kunstpixel

Vår forrige syntetiske generering hadde **to store avvik mot virkeligheten**:
1. Den manglet pandemikrakket i 2020–2021 (viste 181 000 i stedet for ca. 45 000).
2. Den brukte flat billettpris på 120 kr helt tilbake til 2010.

### Korrekt fasit fra Kunstpixels eget arkiv:
For at dagsbesøket skal være 100 % troverdig og stemme med museets historikk, må årsverdiene kalibreres direkte mot `utstillinger_historikk`:
- **2018:** 137 019 besøk
- **2019:** 142 984 besøk
- **2020 (Korona):** **45 847 besøk** (med nedstengte perioder i mars-mai og november)
- **2021 (Korona):** **64 491 besøk**
- **2022 (Rekyl):** 147 507 besøk
- **2023:** 145 217 besøk
- **2024:** 145 156 besøk
- **2025–2026:** ca. 120 000 – 135 000 besøk
