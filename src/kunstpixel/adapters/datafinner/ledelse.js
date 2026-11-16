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
  function etikett(felt) {
    if (ORD[felt]) return ORD[felt];
    var t = String(felt || "").replace(/_/g, " ");
    return t.charAt(0).toUpperCase() + t.slice(1);
  }

  var api = { statusVisning: statusVisning, normaltTekst: normaltTekst, tallPer: tallPer, datoKort: datoKort, etikett: etikett, tall: tall,
    kategoriTekst: kategoriTekst, jaNei: jaNei,
    lesOppfolging: lesOppfolging, merkFulgtOpp: merkFulgtOpp, angreFulgtOpp: angreFulgtOpp, erFulgtOpp: erFulgtOpp,
    grupper: grupper, fristTekst: fristTekst };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else rot.Ledelse = api;
})(this);
