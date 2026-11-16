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
    forrige_uke: "Forrige uke", i_fjor: "I fjor"
  };
  function etikett(felt) {
    if (ORD[felt]) return ORD[felt];
    var t = String(felt || "").replace(/_/g, " ");
    return t.charAt(0).toUpperCase() + t.slice(1);
  }

  var api = { statusVisning: statusVisning, normaltTekst: normaltTekst, tallPer: tallPer, datoKort: datoKort, etikett: etikett, tall: tall };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else rot.Ledelse = api;
})(this);
