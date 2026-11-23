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
Rom 015 i kjelleren ved vareheisen. 8,7 × 10 m, takhøyde 3,8 m. Epoksygulv med ladefelt. Her står sju av de åtte robotene: tre renholdsroboter, to vaktroboter og to transportroboter. Renholdsrobot 3 har fast plass i 2. etasje. Kunstrobotene (hengerobot og to kunstkasser) har også ladeplass her, men er ikke med i dette bildet.
```
Interior of a robot garage and charging room in a museum basement, about 9 by 10 metres, 3.8-metre ceiling.
Hard-wearing light grey epoxy floor with painted charging bays marked by yellow lines. Docked at seven charging
stations: three compact autonomous floor-cleaning robots, two slim security patrol robots with a camera mast, and
two low autonomous transport robots, one with a padded lifting platform for art crates and one with a flat cargo
deck for packaging and tools. A workbench with tools and
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

## Detaljer og bygget i bruk

Disse ti bildene viser rommene mellom salene, hvordan kunsten flyttes, og maskinparken i arbeid. To av dem er nærbilder av materialer. Bruk samme felles stil. Der promptene sier *close-up*, kan kameraet være nærmere enn 1,6 m.

### 14. Monumentaltrappen · `22_monumentaltrapp.jpg`
Rom 108, 1. etasje i hovedfløyen. 2,2 m bred og 12 m lang trapp, takhøyde 6 m. Trinn i hvit Carrara-marmor, håndløper i eik og hvitmalte vegger. Overlyset fra vestibylen faller ned over trappen.
```
Interior photograph looking up a long, straight monumental staircase in a 1912 neoclassical museum, the flight
about 2.2 metres wide and 12 metres long, rising one full storey of 6 metres. Steps of polished white Carrara
marble with slightly worn front edges, a solid oak handrail on dark bronze brackets along both walls. Walls in
smooth white plaster (NCS S 0500-N). Soft daylight falls from a glass roof lantern high above the vestibule at the
top. At the top landing, a glimpse of a light grey terrazzo corridor. One visitor halfway up, seen from behind.
Calm, elegant, a sense of ascent.
```

### 15. Gangbroen i 2. etasje med glassheisen · `23_repos_p2_glassheis.jpg`
Rom 205 og 206, 2. etasje. Øverste trappeavsats og øvre stopp for publikumsheisen. Terrazzo i flukt med gangbroen, rekkverk i glass og børstet stål, åpent opp mot glasstaket.
```
Interior photograph of an upper-floor landing in a museum, where the top of a white marble staircase meets a
gallery bridge. Light grey terrazzo floor running flush onto the landing, which has a solid oak floor section.
A glass passenger lift with a brushed stainless-steel frame stops at the landing; its doors are closed.
Frameless structural glass balustrades with a slim oak handrail. Above, an open void up to a glass roof with
slender steel beams, daylight pouring down. Ceiling height 4.8 metres around the void. White plaster walls with a
recessed oak handrail. A visitor with a stroller waiting for the lift, seen from behind.
```

### 16. Vare- og kunstheisen med transportrobot · `24_kunstheis_transportrobot.jpg`
Rom 004, sjakten går gjennom alle etasjer. Godsheis på 3,5 tonn med innvendige mål 3,2 × 2,2 m. Gulv i riflet aluminium og rustfrie sparkeplater. Transportrobot 1 løfter opptil 400 kg.
```
Photograph from outside an open, large goods lift for artworks in a museum basement. The lift car is 3.2 by
2.2 metres, with a non-slip ribbed aluminium floor and brushed stainless-steel kick plates on the lower walls,
plus padded grey protective blankets hung on the upper walls. Wide steel doors are fully open. Inside, a low
autonomous transport robot with a padded lifting platform carries a closed wooden art crate (labelled only with
a number), strapped down. A museum technician in a dark work jacket stands beside it holding a tablet, seen from
the side, face not visible. A key switch panel by the door. Bright, even, practical lighting.
```

### 17. Kjøreslusa · `25_kjoresluse.jpg`
Rom 011 i kjelleren, sikringssone S4. 3,7 × 12 m, takhøyde 3,8 m. Betong og en port i hver ende. Rampen kommer ned fra bakgården i nord. Kunsttransporten kjører helt inn til kunstmottaket.
```
Interior photograph of a narrow, lockable vehicle airlock in a museum basement, about 3.7 metres wide and
12 metres long, 3.8-metre ceiling. Dust-sealed concrete floor with painted yellow wheel guides, painted concrete
walls, open concrete ceiling with ducts and bright LED strip lights. A small white climate-controlled art-transport
van has just driven in; the outer steel roll-up door behind it is closing, with grey daylight from the ramp
visible under it. At the near end, a second steel roll-up door leads into the art-receiving room and is still
closed. A camera in each corner, a red-and-green traffic light by each door, a card reader on the wall.
Controlled, secure, functional.
```

### 18. Monteringsverkstedet · `26_monteringsverksted.jpg`
Rom 009 i kjelleren under hovedfløyen. 8 × 10 m, takhøyde 3,8 m. Her lages rammer og sokler til utstillingene.
```
Interior photograph of a museum workshop for frames and display plinths in a basement, 8 by 10 metres,
3.8-metre ceiling. Dust-sealed concrete floor with light sawdust near the machines. Painted concrete walls with a
pegboard full of hand tools. A table saw with a dust-extraction hose, a large mitre saw for picture frames, a
spray area behind a clear curtain. Freshly built white plinths of different heights stand in a row, one being
painted. Stacks of oak and pine boards on a wall rack, empty frame profiles hanging on hooks. Bright work lights
under an open concrete ceiling with ducts. One carpenter in ear defenders working at the bench, seen from behind.
```

### 19. Kunstslusa ved Sal E · `27_kunstsluse_sal_e.jpg`
Rom 113, 1. etasje i glassfløyen. 4,7 × 12 m, takhøyde 4,5 m. Mellom vareheisen og Sal E. Kunsten pakkes ut og venner seg til klimaet her før den henges opp.
```
Interior photograph of a narrow art lock and storage room between a goods lift and a temporary-exhibition hall,
4.7 by 12 metres, 4.5-metre ceiling. Dust-sealed concrete floor, painted concrete walls, open ceiling with
ducts. Several opened wooden crates with foam inserts; two large unframed invented textile artworks lie flat on a
padded table wrapped in acid-free tissue. A climate logger on a stand and a wall display glowing green. A wide
double door on one side leads to a white exhibition hall, glimpsed through a gap. Two technicians in cotton gloves
checking a condition report on a tablet. Calm, careful, controlled.
```

### 20. Kontorlandskap for kurator og formidling · `28_kontor_kurator.jpg`
Rom 213, 2. etasje i glassfløyen. 16 × 9,4 m, takhøyde 3,2 m. Linoleum, hvite vegger, akustikkplater og et møterom med glassvegg.
```
Interior photograph of an open-plan museum office for curators and educators, 16 by 9.4 metres, 3.2-metre
ceiling. Warm grey linoleum floor, white walls, acoustic ceiling panels with soft LED lighting. Height-adjustable
desks in light oak, each with a monitor. A large pinboard wall with printed exhibition layouts, small invented
artwork reproductions and colour swatches pinned up. A glass-walled meeting room at the far end with a long table
and a wall screen showing a simple, blurred floor plan with coloured rooms (no readable text). Tall windows with
daylight. Two staff members discussing at a desk, seen from behind. Practical, creative, calm.
```

### 21. Vaktroboten på nattrunde i Sal A · `29_vaktrobot_sal_a_natt.jpg`
Rom 101, 1. etasje i hovedfløyen. 18 × 12 m, takhøyde 6 m. Koksgrå teglvegger, eikeparkett i fiskebein og lanternetak med UV-filter. Vaktrobot 1 går nattrunden i 1. etasje. Vaktrobotene kjører aldri inn i magasinene (S4).
```
Interior photograph of a large, dark gallery hall at night, 18 by 12 metres with a 6-metre ceiling, in a 1912
museum. Walls in rendered brick painted deep charcoal grey (NCS S 8000-N), white-oiled oak herringbone parquet.
The roof lantern overhead is dark blue with night sky. Only dim night lighting: low guide lights near the floor
and faint spotlights on a few invented Nordic romantic landscape paintings – a misty forest, a mountain lake under
a pale summer night, a troll-like rock formation. In the middle of the room, a slim, current-day autonomous
security patrol robot about 1.4 metres tall with a camera mast and a soft blue status light glides across the
parquet, its light reflected in the floor. No people. Quiet, slightly mysterious, realistic, not science fiction.
```

### 22. Renholdsroboten i gangen før åpning · `30_renholdsrobot_gang_glassfloy.jpg`
Rom 114, 1. etasje i glassfløyen. 23,7 × 2,4 m, takhøyde 4,5 m. Lys grå terrazzo og hvite vegger. Gangen går fra hovedfløyen til Sal E, kafeen og toalettene. Nødutgangen i øst går ut mot elvepromenaden.
```
Interior photograph looking down a long, narrow museum corridor in a modern glass wing, about 24 metres long,
2.4 metres wide, 4.5-metre ceiling, early morning before opening. Light grey terrazzo floor with a fresh wet sheen
in a strip behind a small, low autonomous floor-cleaning robot that is working its way down the corridor. White
plaster walls (NCS S 0500-N), acoustic ceiling panels with recessed lights, a green emergency-exit pictogram (no
text) above a glass door at the far end, with soft daylight and a glimpse of a river promenade outside. A side
opening shows part of a café with chairs still on the tables. No people. Fresh, quiet, orderly.
```

### 23. Nærbilde der teglfløyen møter glassfløyen · `31_detalj_fasadeskjot.jpg`
Utvendig nærbilde mot sør. Rød håndbanket tegl, sokkel i Iddefjord-granitt og gesims i sandstein møter strukturelt glass med eikelameller og slipt betong. Gesimsen ligger i samme høyde på begge fløyene.
```
Exterior architectural detail photograph, close-up, of the exact junction where a 1912 museum building meets a
2016 extension. On the left: hand-made red brick with lime mortar joints on a base of grey Iddefjord granite, a
carved sandstone cornice at the top of the frame. On the right: a full-height structural glass façade with slim
vertical light-oak sun-shading fins, standing on a base of pale polished concrete. Between them, a narrow recessed
shadow joint in dark bronze metal; the glass wing's roof edge lines up exactly with the sandstone cornice. The
glass reflects the brick and an overcast Nordic sky. No signs, no text. Crisp, precise detail.
```

---

## Etterpå (for Claude Code)
- Legg bildene inn i `06_kart/bilder/` med filnavnene over.
- Koble dem til rommene i `build_map.py` (`room_images` og galleriet) og i `lag_pdf.py`.
- Utvid `test_tier1_bildegalleri_referansemotiver_integritet` med de nye filene.
- Kjør `test_bilder_uten_gammelt_navn.py`. Se også selv etter tekst i bildene, for testen fanger bare kjente gamle filer.
