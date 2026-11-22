"""Lager bygningsdokumentasjon for Kunstpixel som PDF.

Tall og rom hentes fra 06_kart/bygning_geometri.json (fasit), bildene fra 06_kart/bilder og
plantegningene fra 06_kart/plantegning_*.svg. Microsoft Edge (headless) tegner plantegningene
til PNG og skriver PDF-en. Ingen nye pakker trengs.

Kjør:  py -3.13 02_deliverables/bygningsdokumentasjon/lag_pdf.py
"""

from __future__ import annotations

import base64
import html
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KART = ROOT / "06_kart"
UT = Path(__file__).resolve().parent
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
DATO = "22.11.2026"

DATA = json.loads((KART / "bygning_geometri.json").read_text(encoding="utf-8"))
M = DATA["museum"]
A = M["arealer_ns3940"]

# Bildetekster: hva bildet viser, og hvilket rom i modellen det hører til.
BILDER = {
    "eksterior": [
        ("01_eksterior_hovedfasade.jpg", "Hovedfasaden mot Bispegata",
         "Hovedfløyen fra 1912 i rød tegl på granittsokkel, med mansardtak i irret kobber og monumental "
         "granitt-trapp. Glassfløyen fra 2016 skimtes til venstre, og Nidarosdomens spir står i bakgrunnen."),
        ("01_eksterior_fasade.jpg", "Hovedfløy og glassfløy sett fra plassen",
         "Inngangspartiet med «KUNSTPIXEL 1912» over døra og glassfløyen med egen trinnfri inngang. "
         "Vertikale eikespiler skjermer mot sol."),
        ("02_eksterior_tilbygg_nidelva.jpg", "Glassfløyen ved Nidelva",
         "Tilbygget fra 2016 i glass, lys betong og eikespiler, med inngang til samtidsavdelingen fra "
         "elvepromenaden. De historiske trebryggene ligger langs elva."),
        ("03_eksterior_skulpturhage.jpg", "Skulpturhagen i atriet",
         "Skjermet hage med granittheller, vannspeil og bronseskulpturer mellom de to fløyene. "
         "Merk: teglfasaden på bildet har rundbuer og passer ikke helt med hovedfløyen på de andre bildene."),
    ],
    "interior": [
        ("04_vestibyle_resepsjon.jpg", "Vestibyle og resepsjon (rom 104, P1)",
         "Ankomsthall med overlys i glass, lys terrazzo og skranke i mørk eik. Adgangsporter fører videre til salene."),
        ("02_vestibyle_ankomst.jpg", "Vestibylen sett mot trappa og bokhandelen",
         "Åpent rom over to etasjer med spiraltrapp, galleri i 2. etasje og billettskranke foran bokhandelen."),
        ("05_museumsbutikk.jpg", "Bokhandel (rom 105, P1)",
         "Kunstbøker, kataloger og keramikk i spesialbygde eikehyller med LED-lys."),
        ("06_museumskafe.jpg", "Museumskafé (rom 106, P1)",
         "Kafeen i glassfløyen med 45 sitteplasser og glassvegg mot Nidelva og trebryggene."),
        ("07_sal_a_mytologi.jpg", "Sal A – Mytologi og natur (rom 101, P1)",
         "Museets største sal med 6 m takhøyde, antrasittgrå vegger og fiskebensparkett. Kittelsen og Sohlberg."),
        ("03_sal_a_mytologi.jpg", "Sal A – sett mot neste sal",
         "Samme sal i en annen vinkel, med siktakse gjennom salene og «KUNSTPIXEL» under salnavnet."),
        ("11_sal_d_munch.jpg", "Sal D – Eksistens og modernisme (rom 202, P2)",
         "Karmosinrøde vegger, dempet lys og klimastyrte montre (50 luks) for Munchs papirverk."),
        ("13_magasin_1_hovedlager.jpg", "Magasin 1 – klimastyrt lager (rom 001, U1)",
         "Høysikkerhetssone med rullehyller i stål, hvelvdør og klimadisplay (18,0 °C / 50 % RF)."),
    ],
}

MANGLER_BILDER = [
    ("Sal B – Realisme og samfunn (102)", "P1, utstilling"),
    ("Sal C – Lys, farge og interiør (201)", "P2, utstilling"),
    ("Sal E – Temporær utstilling (103)", "P1, utstilling"),
    ("Kunstmottak og konservering (002)", "U1, høysikkerhet"),
    ("Teknisk rom og klimasentral (003)", "U1, drift"),
    ("Vaktrom og sikkerhetssentral (203)", "P2, drift"),
    ("Personalrom og garderobe (204)", "P2, personal"),
    ("Administrasjon og kontorer (207, 213)", "P2, kontor"),
    ("KI-serverrom (013) og robotgarasje (015)", "U1, maskinpark"),
]

MANGLER_TEGNINGER = [
    ("Fasade nord og vest", "Fasade sør og øst er tegnet; nord (bakgård med rampe) og vest gjenstår."),
    ("Situasjonsplan", "Tomta med skulpturhage, varelevering, kjøresluse og gatene rundt."),
    ("Rømnings- og brannplan", "Rømningsveier, nødutganger og brannceller per etasje."),
    ("Robotenes kjøreveier", "Maskinlaget i kartet viser maskiner per rom; kjøreveier og ladepunkter i gangene gjenstår."),
]


MASKINPARK = json.loads((KART / "maskinpark.json").read_text(encoding="utf-8"))
KATEGORINAVN = {"server": "KI-servere", "robot": "Roboter", "anlegg": "Anlegg (klima, lys, ventilasjon)",
                "sikkerhet": "Sikkerhet (kun lesing for KI)", "heis": "Heiser"}


def _maskinside() -> str:
    """Én side om maskinparken: tall, åpne hendelser og maskinene per kategori."""
    mp = MASKINPARK
    from datetime import date, timedelta
    i_dag = mp["i_dag"]
    def neste(m):
        return (date.fromisoformat(m["sist_service"]) + timedelta(days=m["serviceintervall_dager"])).isoformat()
    per_status = {}
    for m in mp["maskiner"]:
        per_status[m["status"]] = per_status.get(m["status"], 0) + 1
    forfalt = sum(1 for m in mp["maskiner"] if neste(m) < i_dag)
    apne = [h for h in mp["hendelser"] if not h["lukket"]]
    rader = ""
    for kat, navn in KATEGORINAVN.items():
        ms = [m for m in mp["maskiner"] if m["kategori"] == kat]
        rader += f"<tr class=sum><td colspan=5>{navn} ({len(ms)})</td></tr>"
        rader += "".join(
            f"<tr><td>{m['maskin_id'].replace('KP-MASK-', '')}</td><td>{html.escape(m['navn'])}</td><td>{m['rom_id']}</td>"
            f"<td>{m['status'].replace('_', ' ')}</td><td class=n>{neste(m)}</td></tr>" for m in ms)
    hend = "".join(f"<li><b>{h['maskin_id'].replace('KP-MASK-', '')}</b> {h['tidspunkt'].replace('T', ' ')}: "
                   f"{html.escape(h['beskrivelse'])} ({h['alvorlighet']})</li>" for h in apne)
    return f"""<section class=side>
<h2>Maskinpark: KI i drift</h2>
<p class=ingress>{len(mp['maskiner'])} maskiner kan overvåkes og vedlikeholdes via KI. KI-servere står i serverrommet (013) og robotene
har hjemsted i robotgarasjen (015) i kjelleren. KI-en leser tilstand og foreslår kommandoer. Hvert forslag sjekkes mot faste regler
og må godkjennes av driftsansvarlig (og sikkerhetsansvarlig for kritisk utstyr). Ingenting utføres av verktøyene.</p>
<div class=fakta>
 <div><b>{len(mp['maskiner'])}</b><span>maskiner</span></div>
 <div><b>{per_status.get('i_drift', 0)}</b><span>i drift</span></div>
 <div><b>{len(apne)}</b><span>åpne hendelser</span></div>
 <div><b>{forfalt}</b><span>med forfalt service</span></div>
</div>
<h3>Åpne hendelser {i_dag}</h3><ul>{hend}</ul>
<h3>Maskiner</h3>
<table><tr><th>ID</th><th>Maskin</th><th>Rom</th><th>Status</th><th class=n>Neste service</th></tr>{rader}</table>
<p class=liten>Kilde: <code>06_kart/maskinpark.json</code> (syntetisk). Regler: skillen <code>maskinpark</code>. Forbudt for KI uansett: deaktivere slukking, låse opp dører, slå av kamera, alarm eller adgang, overstyre heis.</p>
</section>"""


def _tall(n: float) -> str:
    """Norsk tallformat: mellomrom som tusenskille og komma som desimaltegn (4 350, 4 174,2)."""
    tekst = f"{n:,.1f}" if n != int(n) else f"{int(n):,}"
    return tekst.replace(",", " ").replace(".", ",")


def _b64(sti: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(sti.read_bytes()).decode()


def _edge(*args: str) -> None:
    subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--hide-scrollbars", *args],
                   check=True, capture_output=True, timeout=120)


def tegn_plantegninger(mappe: Path) -> dict[str, Path]:
    """Tegner hver SVG på mørk bakgrunn til PNG (2x oppløsning)."""
    ut = {}
    for kode in ("u1", "p1", "p2"):
        svg = (KART / f"plantegning_{kode}.svg").read_text(encoding="utf-8")
        side = mappe / f"plan_{kode}.html"
        side.write_text(
            "<!doctype html><meta charset='utf-8'><body style='margin:0;background:#0b1220'>"
            f"<div style='width:1100px;height:680px'>{svg}</div></body>", encoding="utf-8")
        png = mappe / f"plan_{kode}.png"
        _edge("--window-size=1100,680", "--force-device-scale-factor=2", f"--screenshot={png}", side.as_uri())
        ut[kode] = png
    # Fasader og snitt (viewBox-bredde 1000 eller 760, høyde 400).
    for navn, bredde in (("fasade_sor", 1000), ("fasade_ost", 760), ("snitt_a", 760), ("snitt_b", 760)):
        svg = (KART / f"{navn}.svg").read_text(encoding="utf-8")
        side = mappe / f"{navn}.html"
        side.write_text("<!doctype html><meta charset='utf-8'><body style='margin:0;background:#0b1220'>"
                        f"<div style='width:{bredde}px;height:400px'>{svg}</div></body>", encoding="utf-8")
        png = mappe / f"{navn}.png"
        _edge(f"--window-size={bredde},400", "--force-device-scale-factor=2", f"--screenshot={png}", side.as_uri())
        ut[navn] = png
    return ut


def _romtabell(etasje: dict) -> str:
    rader = "".join(
        f"<tr><td>{r['romnummer']}</td><td>{html.escape(r['navn'])}</td><td class=n>{r['areal_m2']}</td>"
        f"<td class=n>{r['takhoyde_m']:.1f}</td><td>{r['sikkerhetssone']}</td><td>{r['klimasone']}</td></tr>"
        for r in etasje["rom"])
    sum_rom = sum(r["areal_m2"] for r in etasje["rom"])
    return (f"<table class=rom><tr><th>Rom</th><th>Navn</th><th class=n>m²</th><th class=n>Høyde</th>"
            f"<th>Sikring</th><th>Klima</th></tr>{rader}"
            f"<tr class=sum><td></td><td>Sum rom + fasadevegg mellom fløyene ({_fasade():.2f}) = BRA for etasjen</td>"
            f"<td class=n>{sum_rom + _fasade():.1f}</td><td colspan=3>BRA {etasje['bra_etasje_m2']} m²</td></tr></table>")


def _fasade() -> float:
    f = M["fotavtrykk"]["fasadevegg"]
    return f["b"] * f["d"] / 100


def _bilde(fil: str, tittel: str, tekst: str) -> str:
    return (f"<figure><img src='{_b64(KART / 'bilder' / fil, 'image/jpeg')}'>"
            f"<figcaption><b>{html.escape(tittel)}</b> {html.escape(tekst)}"
            f"<span class=fil>{fil}</span></figcaption></figure>")


def lag_html(planer: dict[str, Path]) -> str:
    eks, inn = BILDER["eksterior"], BILDER["interior"]
    h, t = M["eksterior"]["hovedfløy"], M["eksterior"]["tilbygg_ost"]
    b = M["brannkonsept"]
    etasjer = {e["kode"]: e for e in DATA["etasjer"]}
    sik, kli = DATA["soner_definisjon"]["sikkerhet"], DATA["soner_definisjon"]["klima"]

    plansider = ""
    for kode, navn in (("P1", "1. etasje – hovedplan"), ("P2", "2. etasje – galleri og sikkerhet"), ("U1", "Kjeller – magasin og teknikk")):
        e = etasjer[kode]
        plansider += (
            f"<section class=side><h2>Plantegning {kode}: {navn}</h2>"
            f"<p class=ingress>{html.escape(e['beskrivelse'])} Kote ferdig gulv {e['kote_moh']:.2f} moh "
            f"({e['kote_relativ']}). Tegning {e['tegningsnummer']}, målestokk {e['malestokk']}.</p>"
            f"<img class=plan src='{_b64(planer[kode.lower()], 'image/png')}'>{_romtabell(e)}</section>")

    sonerader = "".join(f"<tr><td><span class=prikk style='background:{s['farge']}'></span>{s['kode']}</td>"
                        f"<td>{html.escape(s['navn'].split('–')[-1].strip())}</td><td>{html.escape(s['beskrivelse'])}</td></tr>"
                        for s in sik.values())
    klimarader = "".join(f"<tr><td><span class=prikk style='background:{k['farge']}'></span>{k['kode']}</td>"
                         f"<td>{k['temp']} · {k['rf']} · {html.escape(k['luks'])}</td><td>{html.escape(k['beskrivelse'])}</td></tr>"
                         for k in kli.values())

    p1sum = sum(r["areal_m2"] for r in etasjer["P1"]["rom"])
    p2sum = sum(r["areal_m2"] for r in etasjer["P2"]["rom"])
    u1sum = sum(r["areal_m2"] for r in etasjer["U1"]["rom"])

    return f"""<!doctype html><html lang=no><head><meta charset=utf-8><title>Kunstpixel – bygningsdokumentasjon</title>
<style>
@page {{ size: A4; margin: 16mm 15mm 16mm 15mm; }}
* {{ box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1f2328; font-size: 10pt; line-height: 1.45; margin: 0; }}
h1 {{ font-family: Georgia, serif; font-weight: normal; font-size: 30pt; margin: 0 0 4pt; letter-spacing: -0.5pt; }}
h2 {{ font-family: Georgia, serif; font-weight: normal; font-size: 17pt; margin: 0 0 6pt; border-bottom: 1.5pt solid #8a2b2b; padding-bottom: 4pt; }}
h3 {{ font-size: 10.5pt; margin: 12pt 0 4pt; color: #8a2b2b; text-transform: uppercase; letter-spacing: 0.6pt; }}
.side {{ page-break-after: always; }}
.side:last-child {{ page-break-after: auto; }}
.ingress {{ color: #444; margin: 0 0 8pt; }}
.over {{ color: #8a2b2b; text-transform: uppercase; letter-spacing: 1.5pt; font-size: 9pt; font-weight: 600; }}
.forside img {{ width: 100%; border-radius: 2pt; margin: 10pt 0; }}
.fakta {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6pt; margin: 8pt 0; }}
.fakta div {{ border-top: 1.5pt solid #8a2b2b; padding-top: 4pt; }}
.fakta b {{ display: block; font-family: Georgia, serif; font-size: 16pt; font-weight: normal; }}
.fakta span {{ font-size: 8.5pt; color: #555; }}
.merk {{ background: #f6f1e7; border-left: 3pt solid #b8862b; padding: 6pt 9pt; font-size: 9pt; margin: 8pt 0; }}
table {{ width: 100%; border-collapse: collapse; font-size: 8.8pt; margin: 4pt 0 6pt; }}
th {{ text-align: left; font-weight: 600; border-bottom: 1pt solid #999; padding: 3pt 4pt; }}
td {{ border-bottom: 0.5pt solid #ddd; padding: 2.5pt 4pt; vertical-align: top; }}
.n {{ text-align: right; }}
tr.sum td {{ font-weight: 600; border-top: 1pt solid #999; border-bottom: none; }}
.to {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10pt 12pt; }}
figure {{ margin: 0; break-inside: avoid; }}
figure img {{ width: 100%; display: block; border-radius: 2pt; }}
figcaption {{ font-size: 8.6pt; color: #333; margin-top: 3pt; }}
figcaption b {{ display: block; color: #1f2328; font-size: 9.2pt; }}
.fil {{ display: block; color: #888; font-size: 7.5pt; font-family: Consolas, monospace; }}
img.plan {{ width: 100%; border-radius: 2pt; margin: 2pt 0 6pt; }}
.prikk {{ display: inline-block; width: 7pt; height: 7pt; border-radius: 50%; margin-right: 4pt; }}
ul {{ margin: 3pt 0 6pt 14pt; padding: 0; }} li {{ margin-bottom: 2pt; }}
.liten {{ font-size: 8pt; color: #666; }}
</style></head><body>

<section class="side forside">
<div class=over>Bygningsdokumentasjon · {DATO}</div>
<h1>Kunstpixel</h1>
<p class=ingress>{html.escape(M['fiktiv_adresse'])} · gnr. {M['matrikkel']['gnr']} / bnr. {M['matrikkel']['bnr']} · Trondheim kommune</p>
<img src='{_b64(KART / 'bilder' / '01_eksterior_hovedfasade.jpg', 'image/jpeg')}'>
<div class=fakta>
 <div><b>{_tall(A['bta_m2'])}</b><span>m² bruttoareal (BTA)</span></div>
 <div><b>{_tall(A['bra_m2'])}</b><span>m² bruksareal (BRA)</span></div>
 <div><b>3</b><span>etasjer: kjeller, hovedplan, galleri</span></div>
 <div><b>1912 · 2016</b><span>hovedfløy og glassfløy</span></div>
</div>
<p>Kunstpixel holder til i et nyklassisistisk museumspalass fra 1912 med en glassfløy fra 2016 mot Nidelva.
Hovedfløyen har fem utstillingssaler fordelt på to plan. I kjelleren ligger klimastyrt magasin, kunstmottak og
teknisk sentral. Dokumentet samler bildene og plantegningene av bygget med beskrivelser, og vurderer til slutt hva som mangler.</p>
<div class=merk>Kunstpixel er et syntetisk demomuseum. Bildene er KI-genererte illustrasjoner, og bygget finnes ikke.
Tall og rom er hentet fra <code>06_kart/bygning_geometri.json</code>, som også brukes av kartet og verktøyet <code>get_building_map_data</code>.</div>
</section>

<section class=side>
<h2>Bygget i tall</h2>
<h3>To fløyer</h3>
<table>
<tr><th></th><th>Hovedfløy</th><th>Glassfløy (tilbygg øst)</th></tr>
<tr><td>Byggeår</td><td>{h['byggeaar']}</td><td>{t['byggeaar']}</td></tr>
<tr><td>Stil</td><td>{html.escape(h['arkitekturstil'])}</td><td>{html.escape(t['arkitekturstil'])}</td></tr>
<tr><td>Fasade</td><td>{html.escape(h['fasade'])}</td><td>{html.escape(t['fasade'])}</td></tr>
<tr><td>Tak</td><td>{html.escape(h['tak'])}</td><td>{html.escape(t['tak'])}</td></tr>
<tr><td>Adkomst</td><td>{html.escape(h['hovedinngang'])}</td><td>{html.escape(t['adkomst'])}</td></tr>
<tr><td>Yttervegg</td><td>{M['veggtykkelser_mm']['yttervegg_eldre_floy']} mm tegl/mur</td><td>{M['veggtykkelser_mm']['yttervegg_tilbygg_ost']} mm betong/glass</td></tr>
</table>
<h3>Arealer (NS 3940)</h3>
<table>
<tr><th></th><th class=n>U1 kjeller</th><th class=n>P1 hovedplan</th><th class=n>P2 galleri</th><th class=n>Sum</th></tr>
<tr><td>BTA (bruttoareal), m²</td><td class=n>{A['etasjefordeling_bta']['U1']}</td><td class=n>{A['etasjefordeling_bta']['P1']}</td><td class=n>{A['etasjefordeling_bta']['P2']}</td><td class=n>{A['bta_m2']}</td></tr>
<tr><td>BRA (bruksareal), m²</td><td class=n>{A['etasjefordeling_bra']['U1']}</td><td class=n>{A['etasjefordeling_bra']['P1']}</td><td class=n>{A['etasjefordeling_bra']['P2']}</td><td class=n>{A['bra_m2']}</td></tr>
<tr><td>Rom + fasadevegg, m²</td><td class=n>{u1sum + _fasade():.1f}</td><td class=n>{p1sum + _fasade():.1f}</td><td class=n>{p2sum + _fasade():.1f}</td><td class=n>{u1sum + p1sum + p2sum + 3 * _fasade():.1f}</td></tr>
<tr><td>Kote ferdig gulv, moh</td><td class=n>{M['matrikkel']['kote_u1_fg_moh']:.2f}</td><td class=n>{M['matrikkel']['kote_p1_fg_moh']:.2f}</td><td class=n>{M['matrikkel']['kote_p2_fg_moh']:.2f}</td><td class=n>gesims {M['matrikkel']['kote_gesims_moh']:.2f}</td></tr>
</table>
<p class=liten>Bebygd areal (BYA) {A['bya_m2']} m² på en tomt på {A['tomteareal_m2']} m² ({A['utnyttelsesgrad_prosent_bya']} % utnyttelse). Terreng {M['matrikkel']['kote_terreng_moh']:.2f} moh.</p>
<h3>Brann og sikring</h3>
<table>
<tr><td>Klasser</td><td>Brannklasse {b['brannklasse']}, risikoklasse {b['risikoklasse']}, bæresystem {b['baeresystem']}, etasjeskiller {b['etasjeskiller']}</td></tr>
<tr><td>Slokking</td><td>{html.escape(b['slokking'])}</td></tr>
<tr><td>Alarm</td><td>{html.escape(b['alarmanlegg'])}</td></tr>
<tr><td>Rømning</td><td>{html.escape(b['romning'])}</td></tr>
<tr><td>Skallsikring</td><td>{html.escape(M['eksterior']['omgivelser']['skallsikring'])}</td></tr>
</table>
<h3>Sikringssoner</h3><table>{sonerader}</table>
<h3>Klimasoner</h3><table>{klimarader}</table>
</section>

<section class=side>
<h2>Eksteriør</h2>
<p class=ingress>{html.escape(M['eksterior']['omgivelser']['by_kontekst'])}</p>
<div class=to>{''.join(_bilde(*x) for x in eks)}</div>
</section>

{plansider}

<section class=side>
<h2>Fasader</h2>
<p class=ingress>Tegnet fra samme modell som planene: bredder fra fotavtrykket og høyder fra kotene. Hovedfløyen har mansardtak
(topp {_tall(M['fotavtrykk']['volumer'][0]['tak_topp_moh'])} moh), glassfløyen flatt sedumtak på gesimshøyde.</p>
<img class=plan src='{_b64(planer["fasade_sor"], "image/png")}'>
<img class=plan style="width:76%" src='{_b64(planer["fasade_ost"], "image/png")}'>
</section>

<section class=side>
<h2>Snitt</h2>
<p class=ingress>Nord–sør-snitt gjennom midten av hver fløy. Snittene viser rommene snittlinja krysser i hver etasje,
etasjeskillerne og kjelleren under terreng.</p>
<img class=plan style="width:76%" src='{_b64(planer["snitt_a"], "image/png")}'>
<img class=plan style="width:76%" src='{_b64(planer["snitt_b"], "image/png")}'>
</section>

<section class=side>
<h2>Interiør: publikumsarealer</h2>
<div class=to>{''.join(_bilde(*x) for x in inn[:4])}</div>
</section>

<section class=side>
<h2>Interiør: saler og magasin</h2>
<div class=to>{''.join(_bilde(*x) for x in inn[4:])}</div>
</section>

{_maskinside()}

<section class=side>
<h2>Vurdering: trenger vi flere bilder og tegninger?</h2>
<p class=ingress><b>Ja.</b> Plantegningene er nå komplette for alle tre etasjer. Bildene dekker fasaden, publikumsarealene, Sal A, Sal D og magasinet. Tre av fem utstillingssaler og alle driftsrommene mangler bilder. Fasade sør og øst og to snitt er tegnet. Fasade nord og vest, situasjonsplan og rømningsplan mangler.</p>
<h3>Bilder som mangler</h3>
<table><tr><th>Rom</th><th>Etasje og type</th></tr>{''.join(f'<tr><td>{a}</td><td>{b_}</td></tr>' for a, b_ in MANGLER_BILDER)}</table>
<h3>Tegninger som mangler</h3>
<table><tr><th>Tegning</th><th>Hva den skal vise</th></tr>{''.join(f'<tr><td>{a}</td><td>{b_}</td></tr>' for a, b_ in MANGLER_TEGNINGER)}</table>
<h3>Avvik som gjenstår</h3>
<ul>
<li><b>Vestibylen:</b> Bildet viser et rom åpent over to etasjer. Tegningene har gulv over hele vestibylen, fordi BTA er 1 450 m² i hver etasje.</li>
<li><b>Glassfløyens side:</b> Dataene og tegningene har glassfløyen i øst. På hovedfasadebildet står den til venstre, på bildet fra plassen til høyre.</li>
<li><b>Skulpturhagen:</b> Teglbygget på bildet har en annen stil (rundbuer) enn hovedfløyen. Hagen er ikke tegnet inn på tomta ennå.</li>
<li><b>Salnavn:</b> HMS-håndboka kaller Sal A «Klassisk kunst», Sal B «Moderne kunst» og Sal C «Grafikk og papir». Kartet og databasen bruker «Mytologi og natur», «Realisme og samfunn» og «Lys, farge og interiør».</li>
<li><b>Dubletter:</b> <code>04_sal_d_munch.jpg</code> = <code>11_sal_d_munch.jpg</code>, og <code>05_magasin_klimastyrt.jpg</code> = <code>13_magasin_1_hovedlager.jpg</code>.</li>
</ul>
<h3>Rettet 22.11.2026</h3>
<ul>
<li>Bygget er tegnet på nytt som 58 × 25 m med to fløyer. Ganger, toaletter, kontorer, rømningstrapp 2, papirarkiv, verksted, KI-serverrom og robotgarasje er lagt inn. Rommene fyller hver etasje helt, og trapper og heiser står på samme sted i alle etasjer.</li>
<li>BRA er regnet fra tegningen: {_tall(A['bra_m2'])} m² ({_tall(A['etasjefordeling_bra']['P1'])} per etasje). BTA {_tall(A['bta_m2'])} og BYA {_tall(A['bya_m2'])} står som før.</li>
<li>Bildene er renset for det gamle navnet, og kunnskapsfila følger tegningene.</li>
</ul>
</section>
</body></html>"""


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mappe = Path(tmp)
        planer = tegn_plantegninger(mappe)
        side = mappe / "kunstpixel_bygning.html"
        side.write_text(lag_html(planer), encoding="utf-8")
        pdf = UT / "kunstpixel_bygning.pdf"
        _edge("--no-pdf-header-footer", f"--print-to-pdf={pdf}", side.as_uri())
    print(f"Skrev {pdf} ({pdf.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    main()
