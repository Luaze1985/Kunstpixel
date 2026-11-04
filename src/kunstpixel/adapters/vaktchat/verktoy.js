// Verktøyene Claude kan kalle i chatten. Samme regler som src/kunstpixel/core/vaktrom.py, regnet på et
// øyeblikksbilde av syntetiske data. Ren JS uten DOM, så Node kan teste den mot Python-koden.
function lagVerktoy(D) {
  var dag = function (s) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(s))) throw new Error("Ugyldig dato: " + s + ". Bruk ÅÅÅÅ-MM-DD.");
    return String(s);
  };
  var tid = function (dato, hhmm) {
    if (!/^\d{2}:\d{2}$/.test(String(hhmm))) throw new Error("Ugyldig klokkeslett: " + hhmm + ". Bruk TT:MM.");
    return new Date(dato + "T" + hhmm + ":00Z").getTime();
  };
  var intervall = function (dato, start, slutt) {
    var a = tid(dato, start), b = tid(dato, slutt);
    if (b <= a) b += 864e5;
    return [a, b];
  };
  var leggTil = function (dato, dager) { return new Date(new Date(dato + "T00:00:00Z").getTime() + dager * 864e5).toISOString().slice(0, 10); };
  var iVindu = function (dato) {
    if (dato < D.vindu[0] || dato > D.vindu[1]) throw new Error("Datoen " + dato + " er utenfor dataene i denne demoen (" + D.vindu[0] + " til " + D.vindu[1] + ").");
  };
  var ansattPaa = {}; D.ansatte.forEach(function (a) { ansattPaa[a.id] = a; });
  var innleidPaa = {}; D.innleide.forEach(function (i) { innleidPaa[i.id] = i; });

  function gyldigeKurs(rader, dato) {
    var ut = {};
    rader.forEach(function (k) {
      if (k.sertifisert_dato <= dato && (!k.gyldig_til || k.gyldig_til >= dato) && !(k.status === "utlopt" && !k.gyldig_til)) {
        (ut[k.id] = ut[k.id] || {})[k.skill_code] = true;
      }
    });
    return ut;
  }
  function fravaerende(dato) {
    var ut = {};
    D.fravaer.forEach(function (f) { if (f.fra <= dato && f.til >= dato) ut[f.id] = f.type; });
    return ut;
  }
  function krav(stasjon) {
    var k = D.krav[stasjon];
    if (!k) throw new Error("Ukjent stasjon: " + stasjon + ". Bruk list_stations for å se stasjonene.");
    return k;
  }
  var harAlle = function (sett, koder) { return koder.every(function (k) { return sett && sett[k]; }); };
  var prisNokkel = function (r) { return [r.timepris_uten_tillegg == null ? 1 : 0, r.timepris_uten_tillegg == null ? 0 : r.timepris_uten_tillegg, r.id]; };
  var sorter = function (a, b) {
    var x = prisNokkel(a), y = prisNokkel(b);
    for (var i = 0; i < 3; i++) { if (x[i] < y[i]) return -1; if (x[i] > y[i]) return 1; }
    return 0;
  };

  function list_stations() {
    return Object.keys(D.krav).sort().map(function (s) {
      return { stasjon: s, krav: D.krav[s].map(function (k) { return { kode: k, navn: D.ferdigheter[k] || k }; }) };
    });
  }

  function get_staffing_candidates(inp) {
    var dato = dag(inp.dato); iVindu(dato);
    var stasjon = String(inp.stasjon), start = String(inp.start), slutt = String(inp.slutt);
    var iv = intervall(dato, start, slutt), koder = krav(stasjon);
    var kurs = gyldigeKurs(D.kurs, dato), borte = fravaerende(dato), ettAar = leggTil(dato, -365);
    var tidligere = {};
    D.vakter.forEach(function (v) { if (v[2] === stasjon && v[3] >= ettAar && v[3] < dato) tidligere[v[1]] = (tidligere[v[1]] || 0) + 1; });
    var egne = [], utilgjengelige = [];
    D.ansatte.forEach(function (a) {
      if (!(a.ansatt_fra <= dato && (!a.ansatt_til || a.ansatt_til >= dato))) return;
      if (!harAlle(kurs[a.id], koder)) return;
      if (borte[a.id]) { utilgjengelige.push({ id: a.id, navn: a.navn, stilling: a.stilling, status: "utilgjengelig", fravaerstype: borte[a.id] }); return; }
      egne.push({ id: a.id, type: "egen", navn: a.navn, stilling: a.stilling, avdeling: a.avdeling, kompetanse: koder.slice(),
        timepris_uten_tillegg: a.timesats_ordinar, prisgrunnlag: a.timesats_ordinar == null ? "Ukjent" : "Virke lønnstrinn " + a.lonnstrinn_virke,
        vakter_paa_stasjonen_siste_12_mnd: tidligere[a.id] || 0, epost: a.epost, telefon: a.telefon });
    });
    var ikurs = gyldigeKurs(D.innleid_kurs, dato);
    var innleide = D.innleide.filter(function (i) {
      return i.status === "Aktiv" && i.avtale_fra <= dato && i.avtale_til >= dato && harAlle(ikurs[i.id], koder);
    }).map(function (i) {
      return { id: i.id, type: "innleid", navn: i.navn, stilling: i.stilling, firma: i.firma, kategori: i.kategori,
        timepris_uten_tillegg: i.timepris_nok, prisgrunnlag: "Avtalt timepris", avtale: i.avtale_fra + " til " + i.avtale_til,
        kontaktperson_firma: D.kontaktpersoner[i.orgnr] || null, kompetanse: koder.slice(), epost: i.epost, telefon: i.telefon };
    });
    egne.sort(sorter); innleide.sort(sorter);
    egne.concat(innleide).forEach(function (r, n) { r.nr = n + 1; });
    return { stasjon: stasjon, dato: dato, start: start, slutt: slutt, vaktlengde_timer: Math.round((iv[1] - iv[0]) / 36e3) / 100,
      krav: koder.map(function (k) { return D.ferdigheter[k] || k; }), egne: egne, innleide: innleide, utilgjengelige: utilgjengelige,
      sortering: "Egne ansatte først, så innleide. Innenfor hver gruppe lavest timepris uten tillegg. Ukjent pris sist." };
  }

  function check_staffing_selection(inp) {
    var dato = dag(inp.dato); iVindu(dato);
    var stasjon = String(inp.stasjon), iv = intervall(dato, String(inp.start), String(inp.slutt)), koder = krav(stasjon);
    var ids = Array.isArray(inp.ids) ? inp.ids.map(String) : [];
    if (!ids.length) throw new Error("Velg minst én kandidat (ids).");
    var hvile = D.grenser.daglig_hvile_timer, dognmaks = D.grenser.dognmaks_timer;
    var kurs = gyldigeKurs(D.kurs, dato), ikurs = gyldigeKurs(D.innleid_kurs, dato), borte = fravaerende(dato);
    var fra = leggTil(dato, -1), til = leggTil(dato, 1);
    var unntatt = {}; (inp.unnta_vakter || []).forEach(function (v) { unntatt[v] = true; });  // vakten man gir fra seg i et bytte
    return { stasjon: stasjon, dato: dato, hviletid_krav_timer: hvile, merknad: "Kontrollen bygger bare på registrerte vakter og fravær.",
      resultater: ids.slice(0, 50).map(function (pid) {
        var mangler = koder.filter(function (k) { return !((innleidPaa[pid] ? ikurs : kurs)[pid] || {})[k]; });
        if (innleidPaa[pid]) {
          var f0 = [mangler.length ? "Mangler gyldig kurs på datoen: " + mangler.join(", ") : "Kurs ok.",
            "Innleid: vakter er ikke registrert hos oss, så overlapp og hviletid kan ikke kontrolleres."];
          return { id: pid, navn: innleidPaa[pid].navn, status: mangler.length ? "avvik" : "delvis", funn: f0 };
        }
        if (!ansattPaa[pid]) return { id: pid, status: "ukjent", funn: ["Finner ingen ansatt eller innleid med denne ID-en."] };
        var funn = [];
        if (mangler.length) funn.push("Mangler gyldig kurs på datoen: " + mangler.join(", "));
        if (borte[pid]) funn.push("Utilgjengelig på datoen (" + borte[pid] + ").");
        D.vakter.forEach(function (v) {
          if (v[1] !== pid || v[3] < fra || v[3] > til || unntatt[v[0]]) return;
          var a = intervall(v[3], v[4], v[5]);
          if (a[0] < iv[1] && iv[0] < a[1]) { funn.push("Overlapper med registrert vakt " + v[0] + " (" + v[3] + " " + v[4] + "–" + v[5] + ", " + v[2] + ")."); return; }
          var timer = (a[1] <= iv[0] ? iv[0] - a[1] : a[0] - iv[1]) / 36e5;
          if (timer < hvile) funn.push("For kort hviletid: " + timer.toFixed(1) + " timer mellom denne og vakt " + v[0] + " (krav " + hvile + " timer, AML § 10-8).");
        });
        var lengde = (iv[1] - iv[0]) / 36e5;
        if (lengde > dognmaks) funn.push("Vakten er " + lengde + " timer, over døgnmaks på " + dognmaks + " timer. Må i så fall merkes som overtid.");
        return { id: pid, navn: ansattPaa[pid].navn, status: funn.length ? "avvik" : "ok", funn: funn.length ? funn : ["Ingen funn."] };
      }) };
  }

  function get_weekend_shift_history(inp) {
    var fra = dag(inp.fra), til = dag(inp.til), stasjon = inp.stasjon ? String(inp.stasjon) : "";
    if (fra < D.vakter_fra) throw new Error("Vaktene i denne demoen starter " + D.vakter_fra + ". Velg fra-dato fra og med den.");
    var per = {};
    D.vakter.forEach(function (v) {
      if (v[3] < fra || v[3] > til || (stasjon && v[2] !== stasjon)) return;
      var wd = new Date(v[3] + "T00:00:00Z").getUTCDay();
      if (wd !== 0 && wd !== 6) return;
      var k = v[1] + "|" + v[2];
      var r = per[k] = per[k] || { ansatt_id: v[1], navn: (ansattPaa[v[1]] || {}).navn, stasjon: v[2], helgevakter: 0, timer: 0, siste_dato: v[3] };
      r.helgevakter++; r.timer = Math.round((r.timer + v[6]) * 10) / 10; if (v[3] > r.siste_dato) r.siste_dato = v[3];
    });
    var rader = Object.keys(per).map(function (k) { return per[k]; }).sort(function (a, b) { return b.helgevakter - a.helgevakter || (a.ansatt_id < b.ansatt_id ? -1 : 1); });
    return { fra: fra, til: til, stasjon: stasjon || "alle", helgevakter_totalt: rader.reduce(function (s, r) { return s + r.helgevakter; }, 0), rader: rader.slice(0, 40) };
  }

  function search_active_contractors(inp) {
    var q = String(inp.query || "").toLowerCase();
    return D.innleide.filter(function (i) {
      return i.status === "Aktiv" && (!q || [i.navn, i.firma, i.stilling, i.kategori].join(" ").toLowerCase().indexOf(q) >= 0);
    }).map(function (i) {
      return Object.assign({}, i, { kurs: D.innleid_kurs.filter(function (k) { return k.id === i.id; }).map(function (k) { return { kurs: D.ferdigheter[k.skill_code] || k.skill_code, gyldig_til: k.gyldig_til, status: k.status }; }) });
    });
  }

  function get_personnel_file(inp) {
    var n = String(inp.ansatt_id || "").trim();
    if (!n) throw new Error("Oppgi ansatt-ID eller navn.");
    var saker = D.personalmapper.filter(function (p) { return p.ansatt_id === n.toUpperCase() || p.navn.toLowerCase().indexOf(n.toLowerCase()) >= 0; });
    return { ansatt_id: n, antall_saker: saker.length, saker: saker };
  }

  // Samme regel som vaktrom.find_employee: treff på starten av et ord i navn, stilling eller avdeling.
  function find_employee(inp, perDato) {
    var s = String(inp.sok || "").trim();
    if (!s) throw new Error("Oppgi navn, ansatt-ID, stilling eller avdeling.");
    var per = perDato || new Date().toISOString().slice(0, 10);
    var re = new RegExp("(?<![0-9a-zæøåA-ZÆØÅ])" + s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i");
    var aktivForst = D.ansatte.slice().sort(function (a, b) {
      var x = a.ansatt_til ? 1 : 0, y = b.ansatt_til ? 1 : 0;
      return x - y || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
    });
    return aktivForst.filter(function (a) {
      return a.id === s.toUpperCase() || re.test(a.navn || "") || re.test(a.stilling || "") || re.test(a.avdeling || "");
    }).slice(0, 15).map(function (a) {
      var dager = (Date.parse(per + "T00:00:00Z") - Date.parse(a.ansatt_fra + "T00:00:00Z")) / 864e5;
      return { ansatt_id: a.id, navn: a.navn, stilling: a.stilling, avdeling: a.avdeling, ansatt_fra: a.ansatt_fra, ansatt_til: a.ansatt_til,
        stillingsprosent: a.stillingsprosent, epost: a.epost, telefon: a.telefon, aktiv: !a.ansatt_til || a.ansatt_til >= per,
        ansiennitet_aar: Math.max(0, Math.floor(dager / 365)),
        kurs: D.kurs.filter(function (k) { return k.id === a.id; }).sort(function (x, y) { return x.skill_code < y.skill_code ? -1 : 1; })
          .map(function (k) { return { kurs: D.ferdigheter[k.skill_code] || k.skill_code, gyldig_til: k.gyldig_til, status: k.status }; }) };
    });
  }

  function get_shifts_for_date(inp) {
    var dato = dag(inp.dato), stasjon = inp.stasjon ? String(inp.stasjon) : "";
    if (dato < D.vakter_fra || dato > D.vindu[1]) throw new Error("Vaktene i denne demoen dekker " + D.vakter_fra + " til " + D.vindu[1] + ".");
    var vakter = D.vakter.filter(function (v) { return v[3] === dato && (!stasjon || v[2] === stasjon); }).map(function (v) {
      var a = ansattPaa[v[1]] || {};
      return { vakt_id: v[0], ansatt_id: v[1], navn: a.navn, stilling: a.stilling, stasjon: v[2], dato: v[3], start: v[4], slutt: v[5], timer: v[6] };
    });
    return { dato: dato, stasjon: stasjon || "alle", antall: vakter.length, vakter: vakter };
  }

  function vaktPaa(id) {
    var v = D.vakter.filter(function (x) { return x[0] === String(id).trim().toUpperCase(); })[0];
    if (!v) throw new Error("Finner ingen vakt med ID " + id + ". Bruk get_shifts_for_date for å finne vakt-ID.");
    return { vakt_id: v[0], ansatt_id: v[1], navn: (ansattPaa[v[1]] || {}).navn, dato: v[3], start: v[4], slutt: v[5], stasjon: v[2] };
  }

  function check_shift_takeover(inp) {
    var v = vaktPaa(inp.vakt_id), ny = String(inp.ansatt_id || "").trim().toUpperCase();
    if (!ansattPaa[ny]) throw new Error("Finner ingen ansatt med ID " + ny + ".");
    if (ny === v.ansatt_id) throw new Error(ansattPaa[ny].navn + " har allerede vakten " + v.vakt_id + ".");
    var k = check_staffing_selection({ stasjon: v.stasjon, dato: v.dato, start: v.start, slutt: v.slutt, ids: [ny] });
    return { vakt: v, tar_over: { ansatt_id: ny, navn: ansattPaa[ny].navn }, status: k.resultater[0].status, funn: k.resultater[0].funn,
      hviletid_krav_timer: k.hviletid_krav_timer, merknad: k.merknad };
  }

  function check_shift_swap(inp) {
    var va = vaktPaa(inp.vakt_a), vb = vaktPaa(inp.vakt_b);
    if (va.ansatt_id === vb.ansatt_id) throw new Error("Begge vaktene tilhører samme person. Et bytte trenger to personer.");
    var retninger = [[va, vb], [vb, va]].map(function (p) {
      var gir = p[0], tar = p[1];
      var r = check_staffing_selection({ stasjon: tar.stasjon, dato: tar.dato, start: tar.start, slutt: tar.slutt, ids: [gir.ansatt_id], unnta_vakter: [gir.vakt_id] }).resultater[0];
      return { ansatt_id: gir.ansatt_id, navn: gir.navn, gir_fra_seg: gir.vakt_id, tar: tar.vakt_id, status: r.status, funn: r.funn };
    });
    return { vakt_a: va, vakt_b: vb, retninger: retninger, status: retninger.every(function (r) { return r.status === "ok"; }) ? "ok" : "avvik",
      hviletid_krav_timer: D.grenser.daglig_hvile_timer, merknad: "Kontrollen bygger bare på registrerte vakter og fravær." };
  }

  function get_employee_reviews(inp) {
    var s = String(inp.ansatt_id || "").trim();
    if (!s) throw new Error("Oppgi ansatt-ID eller navn.");
    var rader = D.samtaler.filter(function (m) {
      var a = ansattPaa[m.ansatt_id] || {};
      return m.ansatt_id === s.toUpperCase() || (a.navn || "").toLowerCase().indexOf(s.toLowerCase()) >= 0;
    }).map(function (m) { var a = ansattPaa[m.ansatt_id] || {}; return Object.assign({ navn: a.navn, stilling: a.stilling }, m); })
      .sort(function (x, y) { return x.dato < y.dato ? 1 : x.dato > y.dato ? -1 : 0; });
    return { sok: s, antall: rader.length, samtaler: rader };
  }

  function lookup_handbook(inp) {
    var ord = String(inp.query || "").toLowerCase().split(/\s+/).filter(Boolean);
    if (!ord.length) throw new Error("Oppgi søkeord.");
    return D.handbok.map(function (h) {
      var tittel = (h.avsnitt_tittel + " " + h.kapittel_tittel + " " + (h.stikkord || "")).toLowerCase(), tekst = (h.innhold || "").toLowerCase();
      var poeng = ord.reduce(function (p, o) { return p + (tittel.indexOf(o) >= 0 ? 3 : 0) + (tekst.indexOf(o) >= 0 ? 1 : 0); }, 0);
      return { h: h, poeng: poeng };
    }).filter(function (x) { return x.poeng > 0; }).sort(function (a, b) { return b.poeng - a.poeng || (a.h.punkt_id < b.h.punkt_id ? -1 : 1); })
      .slice(0, Math.min(Number(inp.limit) || 5, 10)).map(function (x) { return x.h; });
  }

  var S = function (props, req) { return { type: "object", properties: props, required: req || [] }; };
  var VAKT = { stasjon: { type: "string", description: "Nøyaktig stasjonsnavn fra list_stations" }, dato: { type: "string", description: "ÅÅÅÅ-MM-DD" },
    start: { type: "string", description: "TT:MM" }, slutt: { type: "string", description: "TT:MM" } };
  return [
    { name: "list_stations", description: "Alle stasjoner i museet med kurskravene for å stå der. Bruk først når du trenger nøyaktig stasjonsnavn.", run: list_stations },
    { name: "get_staffing_candidates", description: "Kandidater til én vakt: egne ansatte med alle kravene gyldige på datoen, så innleide. Sortert på timepris uten tillegg. Viser også hvem som er utilgjengelige og hvorfor.",
      inputSchema: S(VAKT, ["stasjon", "dato", "start", "slutt"]), run: get_staffing_candidates },
    { name: "check_staffing_selection", description: "Kontroller valgte personer for én vakt: kurs, fravær, overlapp med registrerte vakter, hviletid (AML § 10-8) og døgnmaks.",
      inputSchema: S(Object.assign({ ids: { type: "array", items: { type: "string" }, description: "Ansatt- eller innleid-ID-er" } }, VAKT), ["stasjon", "dato", "start", "slutt", "ids"]), run: check_staffing_selection },
    { name: "get_weekend_shift_history", description: "Helgevakter (lørdag og søndag) per person og stasjon i en periode, flest først.",
      inputSchema: S({ fra: { type: "string" }, til: { type: "string" }, stasjon: { type: "string", description: "Valgfritt" } }, ["fra", "til"]), run: get_weekend_shift_history },
    { name: "search_active_contractors", description: "Aktive innleide med firma, kategori, timepris, avtaleperiode, kontaktinfo og kurs. Fritekstsøk i navn, firma, stilling og kategori.",
      inputSchema: S({ query: { type: "string" } }), run: search_active_contractors },
    { name: "find_employee", description: "Finn ansatte på navn, ID, stilling eller avdeling (f.eks. «HR»). Gir ansettelsesdato, ansiennitet i år, om de er aktive, kontaktinfo og kurs.",
      inputSchema: S({ sok: { type: "string" } }, ["sok"]), run: function (inp) { return find_employee(inp, inp.per_dato); } },
    { name: "get_shifts_for_date", description: "Vaktplanen for én dato: hvem som har vakt, stasjon, start, slutt og vakt-ID. Bruk denne i stedet for å gjette tider.",
      inputSchema: S({ dato: { type: "string", description: "ÅÅÅÅ-MM-DD" }, stasjon: { type: "string", description: "Valgfritt" } }, ["dato"]), run: get_shifts_for_date },
    { name: "check_shift_swap", description: "Sjekk et bytte mellom to registrerte vakter begge veier: kurs, fravær, overlapp og hviletid for hver person. Bruk vakt-ID fra get_shifts_for_date.",
      inputSchema: S({ vakt_a: { type: "string" }, vakt_b: { type: "string" } }, ["vakt_a", "vakt_b"]), run: check_shift_swap },
    { name: "check_shift_takeover", description: "Sjekk om en ansatt kan ta over en registrert vakt: kurs, fravær, overlapp, hviletid og døgnmaks.",
      inputSchema: S({ vakt_id: { type: "string" }, ansatt_id: { type: "string" } }, ["vakt_id", "ansatt_id"]), run: check_shift_takeover },
    { name: "get_employee_reviews", description: "Medarbeidersamtalene til én ansatt (ID eller navn): samlet vurdering, styrker, utviklingsområde, erfaring og ønske om helgevakter.",
      inputSchema: S({ ansatt_id: { type: "string" } }, ["ansatt_id"]), run: get_employee_reviews },
    { name: "lookup_handbook", description: "Søk i museets fem håndbøker (personal, HMS, drift, beredskap, SOP). Gir avsnitt med innhold og lovhjemmel.",
      inputSchema: S({ query: { type: "string" }, limit: { type: "integer" } }, ["query"]), run: lookup_handbook },
    { name: "get_personnel_file", description: "Personalmappen til én ansatt (fortrolige saker), søkt på ansatt-ID eller navn.",
      inputSchema: S({ ansatt_id: { type: "string" } }, ["ansatt_id"]), run: get_personnel_file }
  ];
}
if (typeof module !== "undefined") module.exports = { lagVerktoy: lagVerktoy };
