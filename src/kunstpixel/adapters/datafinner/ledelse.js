/* Rene visningsfunksjoner for ledelsessiden (spec datafinner-ledelse, F2/F4).
   Ingen DOM og ingen lagring her, så de kan testes i Node (tests/test_ledelse_js.py).
   I nettleseren: window.Ledelse. I Node: require(...). */
(function (rot) {
  "use strict";

  // Status fra serveren -> ord og form (af-signal go/check/stop). Ukjent og Stengt får ingen farge, aldri grønt.
  var STATUS = {
    "Normal": { tekst: "Normal", klasse: "go" },
    "Følg med": { tekst: "Følg med", klasse: "check" },
    "Over terskel": { tekst: "Over terskel", klasse: "stop" },
    "Stengt": { tekst: "Stengt", klasse: "" }
  };
  function statusVisning(status) {
    var s = STATUS[status];
    return s ? { tekst: s.tekst, klasse: s.klasse } : { tekst: "Mangler data", klasse: "" };
  }

  // Norsk tallformat: mellomrom som tusenskille, komma som desimaltegn og ekte minus.
  function tall(n, desimaler) {
    var deler = Math.abs(n).toFixed(desimaler || 0).split(".");
    var t = deler[0].replace(/\B(?=(\d{3})+(?!\d))/g, " ") + (deler[1] ? "," + deler[1] : "");
    return (n < 0 ? "−" : "") + t;
  }
  function prosent(p) {
    if (p === 0) return "0 %";
    var heltall = Math.round(p) === p;
    return (p < 0 ? "−" : "+") + tall(Math.abs(p), heltall ? 0 : 1) + " %";
  }
  function normaltTekst(normalt, endringPst) {
    if (normalt === null || normalt === undefined) return "Ingen sammenligning";
    return "Normalt " + tall(Math.round(normalt)) + (endringPst === null || endringPst === undefined ? "" : " · " + prosent(endringPst));
  }

  function tallPer(kl) { return kl ? "Tall per kl. " + kl : ""; }

  var UKEDAG = ["søndag", "mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag"];
  function datoKort(iso) {
    if (!iso) return "";
    var d = iso.split("-").map(Number), dag = new Date(Date.UTC(d[0], d[1] - 1, d[2]));
    return UKEDAG[dag.getUTCDay()] + " " + d[2] + "." + d[1] + ".";
  }

  // Feltnavn i databasen er skrevet uten æøå. Kjente navn slås opp, resten får stor forbokstav og mellomrom.
  var ORD = {
    maaned: "Måned", maned: "Måned", formal: "Formål", formaal: "Formål", aar: "År", ar: "År",
    besok: "Besøk", besok_totalt: "Besøk totalt", ukedag_navn: "Ukedag", mottaker_rolle: "Mottaker",
    er_aapent: "Åpent", aapent: "Åpent", apen: "Åpen", maalgruppe: "Målgruppe", malgruppe: "Målgruppe",
    stoette: "Støtte", sporsmal: "Spørsmål", forslag: "Forslag", losning: "Løsning", lost_dato: "Løst dato",
    neste_kontroll: "Neste kontroll", berort_sal_id: "Berørt sal", alvorlighetsgrad: "Alvorlighetsgrad",
    klokkeslett_start: "Starter", klokkeslett_slutt: "Slutter", inneholder_persondata: "Persondata",
    forrige_uke: "Forrige uke", i_fjor: "I fjor",
    besok_uka: "Besøk i uka", endring_forrige_uke_pst: "Endring mot forrige uke (%)",
    endring_i_fjor_pst: "Endring mot i fjor (%)", driftsmeldinger_aapnet: "Driftsmeldinger åpnet"
  };
  // Kategoriverdier som «klima_og_samling» vises som «Klima og samling». Andre verdier (ID-er, STORE ord) står urørt.
  var ORD_I_VERDI = { kafe: "kafé", hms: "HMS", sykefraver: "sykefravær", aapent: "åpent" };
  function kategoriTekst(v) {
    if (typeof v !== "string" || !/^[a-z0-9]+(_[a-z0-9]+)+$/.test(v)) return v;
    var t = v.split("_").map(function (o) { return ORD_I_VERDI[o] || o; }).join(" ");
    return t.charAt(0).toUpperCase() + t.slice(1);
  }
  function jaNei(b) { return b ? "Ja" : "Nei"; }

  // Oversikt på Hjem (Lars 2026-11-17: «pass på støyen»). Løft fram det som krever oppmerksomhet, legg resten bak ett klikk.
  // Krever oppmerksomhet: status som ikke er normal, eller et problemtall (uten status) som er over null.
  var IKKE_NORMAL = { "Følg med": 1, "Over terskel": 1, "Ukjent": 1 };
  var PROBLEMTALL = { driftsmeldinger: 1, hms_avvik: 1 };
  function delAvvik(d, nokler) {
    var ut = { avvik: [], resten: [] };
    (nokler || []).forEach(function (k) {
      var x = d && d[k]; if (!x) return;
      var harStatus = x.status !== undefined && x.status !== null;
      var avvik = harStatus ? !!IKKE_NORMAL[x.status] : !!PROBLEMTALL[k] && x.verdi > 0;
      ut[avvik ? "avvik" : "resten"].push(k);
    });
    return ut;
  }

  // ---------- «Fulgt opp» (F6). Lagres bare i nettleseren. Lagring som feiler, velter ikke siden. ----------
  var NOKKEL = "kunstpixel.oppfolging.v1";
  function lesOppfolging(lager) {
    try { var d = JSON.parse(lager.getItem(NOKKEL) || "{}"); return d && typeof d === "object" && !Array.isArray(d) ? d : {}; }
    catch (e) { return {}; }
  }
  function skriv(lager, d) { try { lager.setItem(NOKKEL, JSON.stringify(d)); } catch (e) { /* privat vindu o.l. */ } return d; }
  function merkFulgtOpp(lager, id, tid) { var d = lesOppfolging(lager); d[id] = { tid: tid }; return skriv(lager, d); }
  function angreFulgtOpp(lager, id) { var d = lesOppfolging(lager); delete d[id]; return skriv(lager, d); }
  function erFulgtOpp(oppf, id) { return !!(oppf && Object.prototype.hasOwnProperty.call(oppf, id)); }
  var GRUPPER = ["Forfalt", "I dag", "Denne uka", "Senere"];
  function grupper(frister, oppf) {
    var ut = {}; GRUPPER.concat(["Fulgt opp"]).forEach(function (g) { ut[g] = []; });
    (frister || []).forEach(function (f) { (erFulgtOpp(oppf, f.id) ? ut["Fulgt opp"] : ut[f.gruppe] || ut.Senere).push(f); });
    return ut;
  }
  function fristTekst(dager) {
    if (dager === 0) return "I dag";
    var n = Math.abs(dager), ord_ = n === 1 ? "dag" : "dager";
    return dager < 0 ? n + " " + ord_ + " over fristen" : "Om " + n + " " + ord_;
  }
  // ---------- 3b: e-postutkast, «Mine oppfølginger» og «Godta». Bare i nettleseren, ingenting sendes. ----------
  // Utkastet (overskrift og tekst) lages på serveren fra en fast mal (B9). Her blir det bare en mailto-lenke.
  function mailto(utkast) {
    if (!utkast || !utkast.overskrift) return null;
    var tekst = String(utkast.tekst || "").replace(/\r?\n/g, "\r\n");
    return "mailto:?subject=" + encodeURIComponent(utkast.overskrift) + "&body=" + encodeURIComponent(tekst);
  }

  // Egen nøkkel for lista. «Fulgt opp» på frister (kunstpixel.oppfolging.v1) er urørt.
  var LISTE = "kunstpixel.oppfolginger.v1";
  var TYPER = { oppfolging: "Følg opp", avvik: "Avvik", godkjent: "Godkjent" };
  function tekst(v, maks) { return typeof v === "string" ? v.slice(0, maks) : ""; }
  function vask(o) {
    return { id: tekst(o.id, 40), tittel: tekst(o.tittel, 200), type: TYPER[o.type] ? o.type : "oppfolging",
      adresse: tekst(o.adresse, 500), kilde: tekst(o.kilde, 200), opprettet: tekst(o.opprettet, 40),
      lukket: typeof o.lukket === "string" ? o.lukket.slice(0, 40) : null };
  }
  function lesOppfolginger(lager) {
    try { var d = JSON.parse(lager.getItem(LISTE) || "[]"); return Array.isArray(d) ? d.filter(function (o) { return o && typeof o === "object"; }).map(vask) : []; }
    catch (e) { return []; }
  }
  function skrivListe(lager, liste) { try { lager.setItem(LISTE, JSON.stringify(liste)); } catch (e) { /* privat vindu o.l. */ } return liste; }
  function leggTilOppfolging(lager, o, tid) {
    var liste = lesOppfolginger(lager), ny = vask({ tittel: o.tittel, type: o.type, adresse: o.adresse, kilde: o.kilde, opprettet: tid, lukket: null });
    var finnes = liste.filter(function (x) { return !x.lukket && x.type === ny.type && x.adresse === ny.adresse && x.tittel === ny.tittel; })[0];
    if (finnes) return finnes;
    ny.id = "o" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
    liste.push(ny); skrivListe(lager, liste);
    return ny;
  }
  function endre(lager, id, f) { var liste = lesOppfolginger(lager); liste.forEach(function (o) { if (o.id === id) f(o); }); return skrivListe(lager, liste); }
  function lukkOppfolging(lager, id, tid) { return endre(lager, id, function (o) { o.lukket = tid; }); }
  function gjenaapneOppfolging(lager, id) { return endre(lager, id, function (o) { o.lukket = null; }); }
  function nyesteAapne(liste, n) {
    return (liste || []).filter(function (o) { return !o.lukket && o.type !== "godkjent"; })
      .slice().sort(function (a, b) { return a.opprettet < b.opprettet ? 1 : a.opprettet > b.opprettet ? -1 : 0; }).slice(0, n);
  }
  // «Godta» (F8): én post per rapportadresse (rapport + valg). Står som lukket, så den ikke telles som åpen oppgave.
  function godta(lager, adresse, tittel, tid) {
    var liste = lesOppfolginger(lager).filter(function (o) { return !(o.type === "godkjent" && o.adresse === adresse); });
    liste.push(vask({ id: "g" + Date.now().toString(36), tittel: tittel, type: "godkjent", adresse: adresse, opprettet: tid, lukket: tid }));
    return skrivListe(lager, liste);
  }
  function angreGodta(lager, adresse) {
    return skrivListe(lager, lesOppfolginger(lager).filter(function (o) { return !(o.type === "godkjent" && o.adresse === adresse); }));
  }
  function erGodkjent(liste, adresse) { return (liste || []).some(function (o) { return o.type === "godkjent" && o.adresse === adresse; }); }

  // CSV for Excel: semikolon, alt i anførselstegn, BOM. Celler som starter med = + - @ får ' foran (CSV-injeksjon).
  function celle(v) {
    var s = v === null || v === undefined ? "" : String(v);
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return '"' + s.replace(/"/g, '""') + '"';
  }
  function oppfolgingCsv(liste) {
    var linjer = [["Tittel", "Type", "Status", "Opprettet", "Lukket", "Kilde", "Adresse"].map(celle).join(";")];
    (liste || []).forEach(function (o) {
      var status = o.type === "godkjent" ? "Godkjent" : o.lukket ? "Lukket" : "Åpen";
      linjer.push([o.tittel, TYPER[o.type] || "Følg opp", status, o.opprettet, o.lukket, o.kilde, o.adresse].map(celle).join(";"));
    });
    return "﻿" + linjer.join("\r\n");
  }
  function typeTekst(t) { return TYPER[t] || "Følg opp"; }

  function etikett(felt) {
    if (ORD[felt]) return ORD[felt];
    var t = String(felt || "").replace(/_/g, " ");
    return t.charAt(0).toUpperCase() + t.slice(1);
  }

  // ---------- Brukervennlighet (Lars 2026-11-18) ----------
  // Fasit uten rå JSON: get_week_overview(dato 2026-11-18), get_absence_report(år 2025, kvartal 2).
  function verdiTekst(v) { return typeof v === "number" ? (v < 0 ? "−" + Math.abs(v) : String(v)) : String(v); }
  function verktoyTekst(navn, args) {
    if (!navn) return "Ingen ennå";
    var deler = Object.keys(args || {}).map(function (k) { return etikett(k).toLowerCase() + " " + verdiTekst(args[k]); });
    return navn + "(" + deler.join(", ") + ")";
  }
  // Regel med samme etiketter som tabellene og ekte tegn: «R-UKE-01: Endring mot forrige uke (%) ≥ −15».
  var TEGN = { ">=": "≥", "<=": "≤", "!=": "≠", "==": "=" };
  function regelTekst(id, felt, operator, terskel) {
    if (!id) return null;
    return id + ": " + etikett(felt) + " " + (TEGN[operator] || operator) + " " + verdiTekst(terskel);
  }
  // Hjelpeteksten kommer fra verktøyets beskrivelse (den samme som MCP bruker). Datovelgeren viser selv formatet,
  // så «ISO-format 'YYYY-MM-DD'» tas bort der. Setninger som da bare er feltnavnet («Dato.»), tas også bort.
  var ISO = /,?\s*\(?\s*(?:i |på formen |i formatet )?(?:ISO-format\s*)?'?YYYY-MM(?:-DD)?'?\s*\)?/g;
  function hjelpTekst(hjelp, type) {
    if (!hjelp || (type !== "date" && type !== "month")) return hjelp || "";
    return hjelp.replace(ISO, "").split(/\.\s*/).map(function (s) { return s.trim(); })
      .filter(function (s) { return s && s.split(/\s+/).length > 2; })
      .map(function (s) { return s + "."; }).join(" ");
  }
  // «Driften denne uka»: dager som ikke har vært ennå (kommer) vises ikke, og stengte dager står som «Stengt», ikke 0.
  // Andre lister (uten feltet «kommer») står urørt.
  function ukeRader(rader) {
    if (!Array.isArray(rader) || !rader.some(function (r) { return r && "kommer" in r; })) return rader;
    return rader.filter(function (r) { return !r.kommer; }).map(function (r) {
      var k = {}; for (var f in r) k[f] = r[f];
      if (r.aapent === false || r.aapent === 0) k.besok = "Stengt";
      return k;
    });
  }
  // Innlånsfristen (retur når utstillingen slutter) er et forslag Lars ikke har bekreftet. Skjult i Datafinner til da.
  var SKJULTE_FRISTER = { innlan: 1 };
  function skjulFrister(frister) {
    var alle = frister || [], synlige = alle.filter(function (f) { return !SKJULTE_FRISTER[f.type]; });
    return { frister: synlige, skjult: alle.length - synlige.length };
  }
  // Tabellsøk: treff i tabellnavn eller kolonnenavn. Store/små bokstaver, ø/å/æ og mellomrom/understrek likt.
  function sokeform(s) { return String(s || "").toLowerCase().replace(/ø/g, "o").replace(/å/g, "a").replace(/æ/g, "ae").replace(/[\s_]+/g, "_").trim(); }
  function filtrerTabeller(tabeller, sok) {
    var q = sokeform(sok);
    if (!q) return (tabeller || []).slice();
    return (tabeller || []).filter(function (t) {
      return sokeform(t.navn).indexOf(q) >= 0 || (t.kolonner || []).some(function (k) { return sokeform(k).indexOf(q) >= 0; });
    });
  }

  var api = { verktoyTekst: verktoyTekst, regelTekst: regelTekst, hjelpTekst: hjelpTekst, ukeRader: ukeRader,
    skjulFrister: skjulFrister, filtrerTabeller: filtrerTabeller,
    statusVisning: statusVisning, normaltTekst: normaltTekst, tallPer: tallPer, datoKort: datoKort, etikett: etikett, tall: tall,
    kategoriTekst: kategoriTekst, jaNei: jaNei, delAvvik: delAvvik,
    lesOppfolging: lesOppfolging, merkFulgtOpp: merkFulgtOpp, angreFulgtOpp: angreFulgtOpp, erFulgtOpp: erFulgtOpp,
    grupper: grupper, fristTekst: fristTekst,
    mailto: mailto, lesOppfolginger: lesOppfolginger, leggTilOppfolging: leggTilOppfolging, lukkOppfolging: lukkOppfolging,
    gjenaapneOppfolging: gjenaapneOppfolging, nyesteAapne: nyesteAapne, godta: godta, angreGodta: angreGodta,
    erGodkjent: erGodkjent, oppfolgingCsv: oppfolgingCsv, typeTekst: typeTekst };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else rot.Ledelse = api;
})(this);
