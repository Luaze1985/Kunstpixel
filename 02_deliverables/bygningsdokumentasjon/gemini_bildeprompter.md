# Bildeprompter til Gemini – Kunstpixel

Laget 2026-11-22 fra `06_kart/bygning_geometri.json`. Mål, materialer, farger og lys i hver prompt er hentet fra rommets data, så bildene passer med tegningene og PDF-en.

## Slik bruker du dem
1. Åpne Gemini (bildegenerering) og lim inn **Felles stil** først i hver ny samtale, eller sett den foran hver prompt.
2. Lim inn én prompt om gangen. Be om **16:9**.
3. Last ned bildet og gi det filnavnet som står ved prompten. Legg det i `06_kart/bilder/`.
4. Gi beskjed til Claude Code. Da kobles bildene til rommene i kartet og PDF-en, og bildetesten oppdateres.

**Sjekk hvert bilde før du lagrer det:**
- Det står ingen navn på skilt. Bare «KUNSTPIXEL» er lov, og helst ingen tekst i det hele tatt.
- Det finnes ingen kjente malerier eller ekte personer i bildet.
- Materialene og fargen stemmer med beskrivelsen.

Lag bildet på nytt hvis det står feil tekst på et skilt.

---

## Felles stil (lim inn først)

```
Photorealistic architectural interior photography for a Norwegian art museum called Kunstpixel in Trondheim.
Style: calm Scandinavian museum photography, natural colours, soft realistic light, sharp focus, eye-level
camera (about 1.6 m), wide-angle 24 mm lens without distortion, 16:9 landscape, 1376 x 768 pixels.
A few visitors or staff may appear small in the frame, seen from behind or at a distance, no recognisable faces.
All artworks must be invented and generic – never copies of real, famous paintings.
NO text, logos or signage anywhere, except that the word "KUNSTPIXEL" may appear once on a sign if natural.
Never write any other museum name. No watermarks.
```

---

## Utstillingssaler

### 1. Sal B – Realisme og samfunn · `08_sal_b_realisme.jpg`
Rom 102, 1. etasje i hovedfløyen (1912). 13 × 12 m, takhøyde 5,0 m. Lyse varmgrå vegger, eikeplankgulv og spotlys.
```
Interior of a compact, intimate gallery room, 13 by 12 metres with a 5-metre ceiling, inside a 1912 brick museum
building. Walls in smooth plaster painted light warm grey (NCS S 1502-Y). Floor of wide solid oak planks with a
white-oiled finish. Ceiling in acoustic plaster with recessed black track lighting, focused warm spotlights on each
painting (150–200 lux, museum lighting, no daylight). On the walls: large invented oil paintings in the style of
1880s Scandinavian social realism – everyday working life, a harbour, a crowded kitchen, a city street in winter –
in heavy dark wooden frames; the largest canvas is over 2 metres wide and rests on a low wall bracket. A long
dark-oak bench in the middle. Doorway on the near wall leading to a corridor. Quiet, intimate, serious atmosphere.
```

### 2. Sal C – Lys, farge og interiør · `09_sal_c_lys_farge.jpg`
Rom 201, 2. etasje i glassfløyen (2016). 16 × 15 m, takhøyde 4,8 m. Dempet linblå vegg, askeparkett og store sørøstvendte vinduer med gardiner.
```
Interior of a bright gallery room in a modern 2016 glass-and-concrete museum wing, 16 by 15 metres, 4.8-metre
ceiling. Walls in smooth plaster painted muted linen blue (NCS S 2010-B). Floor of wide pale white-oiled ash
parquet. Ceiling with acoustic coffers and adjustable skylight panels. One long wall of tall south-east facing
windows with semi-transparent motorised UV-filtering curtains half drawn, soft morning daylight falling across the
floor. On the solid walls: invented late-19th-century Scandinavian paintings of sunlit interiors, open windows, a
woman reading by a window, coastal light – in gilded and light wooden frames. A small UV sensor on the wall near
the window. Airy, luminous, calm.
```

### 3. Sal E – Temporær utstilling · `10_sal_e_temporaer.jpg`
Rom 103, 1. etasje i glassfløyen. 13 × 12 m, takhøyde 5,0 m. Hvite modulære vegger, industriparkett i eik og åpent gittersystem med lysskinner. Høsten 2026 viser salen samisk samtidskunst.
```
Interior of a flexible temporary-exhibition hall in a modern museum wing, 13 by 12 metres, 5-metre ceiling.
White movable modular display walls (NCS S 0500-N) arranged to create a route through the room, one partly folded
partition wall visible. Floor of natural oak industrial parquet. Open black technical grid ceiling with flexible
lighting tracks and many small spotlights. The current exhibition is contemporary Sámi art: invented contemporary
works – large textile hangings in deep red, blue and yellow, a sculptural installation in birch wood and reindeer
leather, a video projection showing a snowy mountain plateau. Respectful, modern presentation, no stereotypes,
no costumes worn by people. Clean, contemporary gallery feel.
```

---

## Drift og sikkerhet

### 4. Kunstmottak og konservering · `14_kunstmottak.jpg`
Rom 002 i kjelleren under glassfløyen, sikringssone S4. 14 × 12 m, takhøyde 3,8 m. Støvfrie vegger, vinylgulv, konserveringsbenk, UV-stasjon og vareheis.
```
Interior of a museum art-receiving and conservation room in a basement, 14 by 12 metres, 3.8-metre ceiling.
Washable dust-free silicate-painted concrete walls in off-white, light grey antistatic vinyl floor. Ceiling of
metal acoustic cassettes with daylight-balanced light panels. Two closed wooden art crates on low dollies
acclimatising, labelled only with numbers. A long conservation workbench with a magnifying lamp, an easel holding
an unframed invented landscape painting, and a mobile UV examination lamp. A wide steel goods-lift door on one
wall, and a roll-up door to a vehicle airlock on the far wall. Two conservators in white coats and cotton gloves
working at a distance. A small climate display on the wall. Clean, controlled, high-security feel.
```

### 5. Teknisk rom og klimasentral · `15_klimasentral.jpg`
Rom 003 i kjelleren. 19,6 × 10 m, takhøyde 3,8 m. Ventilasjonsaggregat, dampbefukter, kjølemaskin og UPS.
```
Interior of a museum building's technical plant room in a basement, about 20 by 10 metres, 3.8-metre ceiling.
Floor of dust-sealed concrete with a floor drain. Walls of bare concrete and old red brick. Exposed ducts, cable
trays and insulated pipes along the ceiling. A large grey air-handling unit with a rotary heat-recovery wheel
(inspection door open), a steam humidifier cabinet, a water chiller, and a row of UPS battery cabinets with green
status lights. A wall-mounted touchscreen showing simple temperature and humidity graphs (no readable text).
Clean, well-maintained, industrial; one technician checking a panel in the background.
```

### 6. Vaktrom og sikkerhetssentral · `16_vaktrom.jpg`
Rom 203, 2. etasje i hovedfløyen. 12 × 10 m, takhøyde 3,2 m. Hevet datagulv, CCTV-vegg, brannsentral og observasjonsglass.
```
Interior of a museum security control room, 12 by 10 metres, 3.2-metre ceiling. Raised access floor with grey
antistatic vinyl. Sound-absorbing wall panels in dark grey, and one internal window of thick bulletproof
observation glass. A large video wall of 12 screens showing invented, blurred camera views of gallery rooms,
corridors and a loading bay (no readable text, no recognisable people). A curved control desk with two
ergonomic chairs, keyboards, a red emergency telephone, a fire-alarm control panel and a key-management cabinet.
Glare-free LED lighting, calm blue tones. One guard seen from behind. 24/7 operations atmosphere.
```

### 7. Personalrom og garderobe · `17_personalrom.jpg`
Rom 204, 2. etasje i hovedfløyen. 18 × 10 m, takhøyde 3,2 m. Linoleum, varmhvite vegger med eikefinér, hvilesone og kjøkkenkrok.
```
Interior of a staff break room and locker area in a museum, 18 by 10 metres, 3.2-metre ceiling. Warm acoustic
linoleum floor. Walls painted warm white with oak-veneer cabinet modules and a row of personal lockers. A small
kitchenette with a coffee machine and sink. A rest zone with two recliner chairs and a low sofa for staff who stand
all day. A large table with chairs. Indirect warm white lighting from acoustic ceiling panels, and a window with
a view over old Trondheim rooftops. Cosy, practical, quiet.
```

### 8. Magasin 2 – papirarkiv · `18_magasin_2_papirarkiv.jpg`
Rom 006 i kjelleren, klimasone K1 (18 °C, 50 % RF, maks 50 luks), sikringssone S4.
```
Interior of a climate-controlled museum archive for works on paper in a basement, 10 by 12 metres,
3.8-metre ceiling. Rows of grey steel plan chests with wide flat drawers, one drawer half open showing acid-free
folders. Mobile compact shelving with archival boxes. Dust-sealed concrete floor, painted concrete walls, exposed
concrete ceiling with inert-gas fire suppression nozzles and cable trays. Very dim, even light (about 50 lux).
A wall-mounted climate display glowing green. Calm, precise, protected.
```

---

## Maskinpark (KI i drift)

### 9. KI-serverrom · `19_ki_serverrom.jpg`
Rom 013 i kjelleren under glassfløyen. 9 × 10 m, takhøyde 3,8 m. GPU-noder, lagring, nettverk, UPS og kjøling i rad.
```
Interior of a small, modern on-premise AI server room in a museum basement, 9 by 10 metres, 3.8-metre ceiling.
Raised floor with perforated tiles and a clear hot-aisle/cold-aisle layout. Two rows of black server racks with
GPU nodes, a storage array and a network core, blue and green status LEDs, neat cable management. An in-row cooling
unit between the racks and a UPS cabinet at the end. Ceiling with cable trays and inert-gas fire suppression
nozzles. Painted concrete walls. One technician with a laptop on a cart at the end of the aisle, seen from behind.
Clean, cool, high-tech but realistic, not science fiction.
```

### 10. Robotgarasje og ladestasjon · `20_robotgarasje.jpg`
Rom 015 i kjelleren ved vareheisen. 8,7 × 10 m, takhøyde 3,8 m. Epoksygulv med ladefelt, renholds-, vakt- og transportroboter.
```
Interior of a robot garage and charging room in a museum basement, about 9 by 10 metres, 3.8-metre ceiling.
Hard-wearing light grey epoxy floor with painted charging bays marked by yellow lines. Docked at six charging
stations: four compact autonomous floor-cleaning robots, two slim security patrol robots with a camera mast, and
one low autonomous transport robot with a padded lifting platform for art crates. A workbench with tools and
spare brushes, wheels and batteries on shelves. Painted concrete walls, acoustic ceiling panels. Open double door
towards a corridor and a steel goods-lift door. Realistic, current-day service robots, not humanoid.
```

---

## Utvendig (erstatter bilder som ikke stemmer)

### 11. Hovedfasaden mot Bispegata, riktig side · `01_eksterior_hovedfasade_v2.jpg`
Erstatter `01_eksterior_hovedfasade.jpg`. Der står glassfløyen til venstre, men den skal stå til høyre, i øst, når du ser fasaden fra gata.
```
Exterior architectural photograph of a Norwegian art museum on a cobbled street in central Trondheim, seen from
the south across the street. On the LEFT: a 1912 neoclassical museum palace, 34 metres wide, two tall storeys,
red hand-made brick on a grey granite base, sandstone cornices, a patinated green copper mansard roof, a monumental
granite staircase up to double oak doors in the centre. On the RIGHT (east), attached to it: a 2016 modern wing,
24 metres wide, same cornice height, full-height structural glass with vertical light-oak fins and pale polished
concrete. The cathedral spire of Nidaros is visible in the distance to the left (west). Overcast Nordic light,
a few pedestrians. Optional single sign "KUNSTPIXEL" above the door, no other text.
```

### 12. Skulpturhagen mellom fløyene · `03_eksterior_skulpturhage_v2.jpg`
Erstatter `03_eksterior_skulpturhage.jpg`. Teglbygget der har rundbuer og en annen stil enn hovedfløyen.
```
Exterior photograph of a small enclosed sculpture garden between two museum wings in Trondheim. On the left the
side wall of a 1912 neoclassical red-brick museum building with tall rectangular white-framed windows, sandstone
cornice and a green copper mansard roof (no round arches). On the right the glass façade of a 2016 wing with
vertical light-oak fins. Granite paving, a low black granite reflecting pool, lawns and ornamental grasses, five
invented abstract bronze sculptures on stone plinths. Summer daylight, a few visitors at a distance.
```

### 13. Bakgården i nord med rampe og kjøresluse · `21_eksterior_bakgard_nord.jpg`
Nytt motiv. Dette er nordsiden av bygget, med rampen ned til kunstmottaket i kjelleren.
```
Exterior photograph of the north side (rear yard) of a museum in central Trondheim. On the left the plain rear
brick façade of a 1912 museum wing with a copper mansard roof; on the right the rear of a 2016 glass-and-concrete
wing. A concrete vehicle ramp leads down to a lockable steel roll-up door into the basement art-receiving area.
A small white climate-controlled art-transport van is parked at the top of the ramp. Bollards, security cameras on
the walls, a gate to the street. Overcast weather, wet asphalt, realistic and functional.
```

---

## Etterpå (for Claude Code)
- Legg bildene inn i `06_kart/bilder/` med filnavnene over.
- Koble dem til rommene i `build_map.py` (`room_images` og galleriet) og i `lag_pdf.py`.
- Utvid `test_tier1_bildegalleri_referansemotiver_integritet` med de nye filene.
- Kjør `test_bilder_uten_gammelt_navn.py`. Se også selv etter tekst i bildene, for testen fanger bare kjente gamle filer.
