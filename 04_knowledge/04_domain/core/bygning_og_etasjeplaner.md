# Bygnings- og etasjeplaner for Kunstpixel (kunstpixel.com)
## Hovedfløy fra 1912 og glassfløy fra 2016: romdisponering, kapasitet og teknisk sikring

> Fasit for mål, rom og soner er `06_kart/bygning_geometri.json`. Den samme modellen brukes av
> kartet (`06_kart/index.html`), plantegningene og verktøyet `get_building_map_data`.
> Arealene regnes ut og kontrolleres av `06_kart/geometri.py` (tester: `tests/test_bygning_geometri.py`).
> Personkapasiteten per sal står i HMS-håndboka (`01_governance/handboker/02_hms_sikkerhetshandbok.md`).
> Tegnet på nytt 2026-11-22 (spec: `docs/specs/2026-11-22-bygg-tegninger-design.md`).

---

### Bygget

| | Hovedfløy (vest) | Glassfløy (øst, mot Nidelva) |
|---|---|---|
| Byggeår | 1912 | 2016 |
| Mål | 34,0 × 25,0 m | 24,0 × 25,0 m |
| Stil | Nyklassisistisk museumspalass | Skandinavisk modernisme |
| Fasade | Rød håndbanket tegl på granittsokkel, gesimser i sandstein | Strukturelt glass med solskjermingslameller og lys slipt betong |
| Tak | Mansardtak med patinert kobber og overlys med UV-filter | Sedumtak med overvannshåndtering |
| Yttervegg | 400 mm tegl/mur | 300 mm betong/glass |

- **Adresse (fiktiv):** Bispegata 9B, 7012 Trondheim, gnr. 401 / bnr. 12. Bispegata ligger i sør, bakgården med rampe i nord, og Nidelva i øst.
- **Samlet:** 58,0 × 25,0 m. Den gamle østfasaden fra 1912 står igjen som 400 mm innervegg mellom fløyene.
- **Arealer (NS 3940):**
  - BTA 4 350 m² (1 450 per etasje).
  - BYA 1 450 m².
  - BRA 4 174,2 m² (1 391,4 per etasje). BRA er regnet fra tegningen: BTA minus yttervegger.
  - Tomt 3 200 m².
- **Etasjer og koter:** U1 kjeller (kote 9,30), P1 hovedplan (kote 13,50), P2 galleri (kote 19,80). Gesims kote 24,90.
- **Brann:**
  - Brannklasse BKL 3, risikoklasse RKL 5.
  - Pre-action vanntåke/sprinkler i publikumsarealer.
  - Inergen-gasslukking i magasinene, kunstmottaket og teknisk sentral.
- **Trapper og heiser** (de samme stedene i alle etasjer de går gjennom):
  - **Hovedtrapp** i hovedfløyen. I U1 er den et låst trapperom bare for ansatte.
  - **Rømningstrapp 2** i glassfløyen, med utgang til bakgården.
  - **Publikumsheis** mellom P1 og P2.
  - **Vare- og kunstheis** (3,5 tonn) fra U1 til P2.

---

```text
=======================================================================================
        KUNSTPIXEL – HOVEDFLØY 1912 (VEST, 34 m)  |  GLASSFLØY 2016 (ØST, 24 m)
=======================================================================================
 Vest / mot Nidarosdomen          Nord: bakgård og rampe             Øst / mot Nidelva

---------------------------------------------------------------------------------------
                       P1 · 1. ETASJE / HOVEDPLAN (kote 13,50)
---------------------------------------------------------------------------------------
+------------------+--------------+--+  ||  +--------+------+-----------------+
| 101 SAL A        | 102 SAL B    |T |  ||  |111 VARE| 113  | 103 SAL E       |
| Mytologi og natur| Realisme og  |R |  ||  |HEIS    |KUNST-| Temporær        |
| 216 m² · h 6,0 m | samfunn      |A |  ||  +--------+SLUSE | 156 m²          |
| maks 50 pers     | 156 m²       |P |  ||  |112 TRAPP 2|   | maks 60 pers    |
+------------------+--------------+P-+  ||  +--------+------+-----------------+
|        109 GANG (2,2 m) øst–vest     |  ||  |        114 GANG                |
+----------------+-------------------+--+  ||  +-------+------+-----------------+
| 105 BOKHANDEL  | 104 VESTIBYLE     |107|  ||  |115 WC/| 116  | 106 MUSEUMSKAFÉ |
| 140 m²         | 160 m² · billett  |HEIS  ||  |GARDE- |KJØK- | 140 m² · 45 sitte- |
|                |                   |110|  ||  |ROBE   |KEN   | plasser, mot elva  |
+----------------+-------------------+---+  ||  +-------+------+-----------------+
                   [ HOVEDINNGANG FRA BISPEGATA ]

---------------------------------------------------------------------------------------
                       P2 · 2. ETASJE / GALLERI (kote 19,80)
---------------------------------------------------------------------------------------
+------------------+--------------+--+  ||  +--------+--+--------------------+
| 202 SAL D        | 207 ADMINI-  |T |  ||  |210 VARE|F | 213 KONTORER,      |
| Eksistens og     | STRASJON     |R |  ||  |HEIS    |O | KURATOR, MØTEROM   |
| modernisme       | 156 m²       |A |  ||  +--------+R | 150,4 m²           |
| 216 m² · RVR 1   |              |P |  ||  |211 TRAPP 2+--------------------+
+------------------+--------------+P-+  ||  +-----------+ 201 SAL C          |
|        208 GANG                      |  ||  | 214 GANG  | Lys, farge og      |
+----------------+-------------------+--+  ||  +-----------+ interiør           |
| 204 PERSONALROM| 203 VAKTROM       |205|  ||  | 215 WC /  | 240 m² · sørøst-   |
| & GARDEROBE    | & SIKKERHETS-     |HEIS  ||  | LAGER     | vendte vinduer     |
| 180 m²         | SENTRAL · 120 m²  |209 SIK|  ||  | 77 m²     | maks 35 pers       |
+----------------+-------------------+---+  ||  +-----------+--------------------+

---------------------------------------------------------------------------------------
                       U1 · KJELLER (kote 9,30)
---------------------------------------------------------------------------------------
+-------------------+------------+--+  ||  +--------+------------------+----+
| 001 MAGASIN 1     | 006 MAGASIN|T |  ||  |004 VARE| 002 KUNSTMOTTAK  |011 |
| 252 m² · 200 verk | 2 – PAPIR- |R |  ||  |HEIS    | & KONSERVERING   |KJØ-|
| K1: 18 °C, 50 % RF| ARKIV 120 m²|A |  ||  +--------+ 168 m²           |RE- |
| Inergen           |            |P |  ||  |005 TRAPP 2                |SLU-|
+-------------------+------------+P-+  ||  +--------+------------------+SE--+
|        008 GANG (drift)             |  ||  |        012 GANG                 |
+---------+--------+-------------------+  ||  +--------------------------+------+
| 009     | 010    | 003 TEKNISK ROM &  |  ||  | 013 KI-     | 015 ROBOT- | 014  |
| VERK-   | REN-   | KLIMASENTRAL       |  ||  | SERVERROM   | GARASJE    |LAGER |
| STED    | HOLD   | 196 m²             |  ||  | 90 m²       | 87 m²      |60 m² |
+---------+--------+--------------------+  ||  +--------------------------+------+
```
(Skissen er ikke i målestokk. Nøyaktige mål står i `bygning_geometri.json` og plantegningene `06_kart/plantegning_*.svg`.)

---

### Nøkkeldetaljer
1. **Sal A (101):** Museets største sal, 6 m takhøyde, mørk antrasitt vegg og dagslys gjennom takvinduer med UV-filter.
2. **Sal D (202):** Sikringssone med EI 60-ståldør og restverdiredning (RVR) nivå 1 for *Skrik*. Papirverk står i klimastyrte montre (K1).
3. **Sal C (201):** Ligger i glassfløyen med sørøstvendte vinduer og gardinstyring mot UV.
4. **Kafeen (106):** Ligger i glassfløyen mot Nidelva og trebryggene, med 45 sitteplasser og kjøkken vegg i vegg.
5. **Kunsttransport:**
   - Kunsten kommer inn fra bakgården via kjøreslusen (011) til kunstmottaket (002) og videre med vareheisen.
   - På P1 går den via kunstslusen (113) til Sal E.
   - I salene flyttes den utenom åpningstid.
6. **Maskinpark (013 og 015):**
   - **KI-serverrom (013, 90 m²)** og **robotgarasje med ladestasjoner (015, 87 m²)** ligger inntil klimasentralen og vareheisen.
   - Hele maskinparken har 40 maskiner: KI-servere, renholds-, vakt-, transport- og kunstroboter, klima, lys, ventilasjon, Inergen, adgang, CCTV og heiser.
   - Fasit: `06_kart/maskinpark.json`. Regler og arbeidsmåte: skillen `maskinpark` (`.claude/skills/maskinpark/SKILL.md`).
   - KI-en leser og foreslår. Et menneske godkjenner, og ingenting utføres av verktøyene.
7. **Universell utforming:** Publikumsheisen ligger ved vestibylen. Toaletter og HC-toalett finnes i begge publikumsetasjer.
