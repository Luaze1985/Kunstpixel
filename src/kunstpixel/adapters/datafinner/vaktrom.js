// Vaktrommet: fem steg (vakt, historikk, kandidater, kontroll, kontakt og utkast).
// Brukes av vaktrom.html (hele siden) og av ett-vindu.html (midten av vinduet). Logikken er den samme begge steder.
//
// Vaktrom.start(opt) returnerer { gaa(stegId), steg: [[id, navn], ...] }. Alle valg er frivillige:
//   rot        element som inneholder vaktrom-markupen (standard: document)
//   stegliste  <ol> for stegmenyen. null = ingen meny her (skallet lager sin egen)
//   mobilvalg  <select> for steg i mobilvisning. null = ingen
//   navRot     der stegmenyens .af-flow-link markeres som gjeldende (standard: document)
//   rolle      funksjon som gir rollen (standard: velgeren #rolle i siden)
//   startSteg  steget som vises først (standard: «kontakt» ved #utkast, ellers «vakt»)
//   vedVakt    kalles med en kort tekst når vakten er valgt
//   vedSteg    kalles med steg-ID hver gang et nytt steg vises
//   vedKall    kalles med (verktøy, args) før hvert kall, så fasiten kan vises
window.Vaktrom = {
  start: function (opt) {
    opt = opt || {};
    var rot = opt.rot || document;

    // Én kilde til tekst og regler.
    var TEKST = {
      lagringsnokkel: "kunstpixel.vaktrom.v1",
      ingenTilgang: "",
      kiAv: "KI er av. Rapportene og den manuelle kontaktflyten virker likevel.",
      kiPa: "KI er på: ",
      ukjentPris: "Ukjent pris"
    };
    var STEG = [["vakt", "Vakt"], ["historikk", "Historikk"], ["kandidater", "Kandidater"], ["kontroll", "Kontroll"], ["kontakt", "Kontakt og utkast"]];

    var $ = function (id) { return rot.querySelector("#" + id); };
    var kiPaa = false, stasjoner = [], roller = [], kand = null, valgt = {}, vakt = null;

    function el(tag, cls, tekst) {
      var e = document.createElement(tag);
      if (cls) e.className = cls;
      if (tekst !== undefined && tekst !== null) e.textContent = tekst;
      return e;
    }
    function sett(id, tekst) { var e = $(id); if (e) e.textContent = tekst; }  // feltet finnes ikke i alle visninger
    function kr(n) { return n === null || n === undefined ? TEKST.ukjentPris : Number(n).toLocaleString("nb-NO") + " kr/t"; }
    function feil(m) { $("feil-tekst").textContent = m || ""; $("feil").hidden = !m; }
    function hent(navn, args) {
      if (opt.vedKall) opt.vedKall(navn, args || {});
      return fetch("/api/verktoy?navn=" + encodeURIComponent(navn) + "&args=" + encodeURIComponent(JSON.stringify(args || {})))
        .then(function (r) { return r.json().then(function (b) { if (!r.ok) throw new Error(b.error || "Ukjent feil"); return b.resultat; }); });
    }
    function post(url, kropp) {
      return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(kropp) })
        .then(function (r) { return r.json().then(function (b) { if (!r.ok) throw new Error(b.error || "Ukjent feil"); return b; }); });
    }
    function rolleNavn() { return opt.rolle ? opt.rolle() : ($("rolle") ? $("rolle").value : ""); }

    // Lokal lagring i nettleseren. Kan mangle (privat vindu), så alt er pakket inn.
    function lesLager() { try { return JSON.parse(localStorage.getItem(TEKST.lagringsnokkel)) || { utkast: [] }; } catch (e) { return { utkast: [] }; } }
    function skrivLager(d) { try { localStorage.setItem(TEKST.lagringsnokkel, JSON.stringify(d)); return true; } catch (e) { return false; } }

    // Avkrysninger per vakt, så de overlever omlasting.
    function vaktNokkel() { return [vakt.stasjon, vakt.dato, vakt.start, vakt.slutt].join("|"); }
    function lagreValg() {
      var d = lesLager(); d.valg = d.valg || {};
      d.valg[vaktNokkel()] = Object.keys(valgt);
      skrivLager(d);
    }

    // Navigasjon
    var ol = opt.stegliste !== undefined ? opt.stegliste : $("stegliste");
    var mob = opt.mobilvalg !== undefined ? opt.mobilvalg : $("mobilvalg");
    function byggSteg() {
      STEG.forEach(function (s, i) {
        if (ol) {
          var li = el("li"), a = el("a", "af-flow-link"); a.href = "#" + s[0]; a.dataset.id = s[0];
          a.appendChild(el("span", "af-step-dot", String(i + 1)));
          a.appendChild(el("span", null, s[1]));
          a.addEventListener("click", function (e) { e.preventDefault(); gaa(s[0]); });
          li.appendChild(a); ol.appendChild(li);
        }
        if (mob) { var o = el("option", null, s[1]); o.value = s[0]; mob.appendChild(o); }
      });
      if (mob) mob.addEventListener("change", function () { gaa(mob.value); });
    }
    function gaa(id) {
      if (id !== "vakt" && id !== "kontakt" && !vakt) { feil("Velg vakt først."); id = "vakt"; }
      if (id === "kandidater" && !kand) return visKandidater();
      if (id === "kontakt") tegnUtkast();
      STEG.forEach(function (s) { $(s[0]).hidden = s[0] !== id; });
      (opt.navRot || document).querySelectorAll(".af-flow-link").forEach(function (a) {
        if (a.dataset.id === id) a.setAttribute("aria-current", "step"); else a.removeAttribute("aria-current");
      });
      if (mob) mob.value = id;
      if (opt.vedSteg) opt.vedSteg(id);
      var t = $(id).querySelector(".af-title"); if (t) t.focus({ preventScroll: true });
      window.scrollTo(0, 0);
    }

    // Steg 1: vakt
    function tegnKrav() {
      var s = stasjoner.filter(function (x) { return x.stasjon === $("stasjon").value; })[0];
      $("krav").textContent = s ? "Krav på stasjonen: " + s.krav.map(function (k) { return k.navn; }).join(", ") + "." : "";
    }
    // Uten sperrer (spec vaktrom-uten-sperrer): alle roller slipper inn.
    function harTilgang() { return true; }
    function sjekkRolle() {
      var ok = harTilgang();
      $("ingen-tilgang").hidden = ok; $("ingen-tilgang").textContent = ok ? "" : TEKST.ingenTilgang;
      $("til-historikk").disabled = !ok;
    }
    function lesVakt() {
      var v = { rolle: rolleNavn(), stasjon: $("stasjon").value, dato: $("dato").value, start: $("start").value, slutt: $("slutt").value };
      if (!v.stasjon || !v.dato || !v.start || !v.slutt) throw new Error("Fyll inn stasjon, dato, start og slutt.");
      return v;
    }
    function oppsummer(v) { return v.stasjon + ", " + v.dato + " kl. " + v.start + "–" + v.slutt + "." + (v.rolle ? " Rolle: " + v.rolle + "." : ""); }
    function settVakt() {
      vakt = lesVakt(); kand = null; valgt = {};
      sett("vakt-oppsummert", oppsummer(vakt)); if (opt.vedVakt) opt.vedVakt(oppsummer(vakt));
      var d = new Date(vakt.dato + "T12:00:00"), f = new Date(d); f.setFullYear(d.getFullYear() - 1); f.setDate(f.getDate() + 1);
      var iso = function (x) { return x.toISOString().slice(0, 10); };
      var t = new Date(d); t.setDate(t.getDate() - 1);
      $("fra").value = iso(f); $("til").value = iso(t);
    }

    // Steg 2: historikk
    function visHistorikk() {
      feil("");
      var st = $("hist-stasjon").value === "valgt" ? vakt.stasjon : "";
      var args = { fra: $("fra").value, til: $("til").value }; if (st) args.stasjon = st;
      return hent("get_weekend_shift_history", args).then(function (h) {
        var k = $("hist-tall"); k.textContent = "";
        [["Personer", h.antall_personer], ["Helgevakter", h.helgevakter_totalt], ["Periode", h.fra + " – " + h.til]].forEach(function (n) {
          var d = el("div", "af-kpi"); d.appendChild(el("p", "af-kpi-label", n[0])); d.appendChild(el("p", "af-kpi-value", String(n[1]))); k.appendChild(d);
        });
        var tb = $("hist-tabell").tBodies[0]; tb.textContent = "";
        h.rader.forEach(function (r) {
          var tr = el("tr");
          [r.navn, r.stilling, r.stasjon, r.helgevakter, r.timer, r.siste_dato].forEach(function (v) { tr.appendChild(el("td", null, String(v))); });
          tb.appendChild(tr);
        });
        if (!h.rader.length) { var tr0 = el("tr"), td = el("td", null, "Ingen helgevakter i perioden."); td.colSpan = 6; tr0.appendChild(td); tb.appendChild(tr0); }
      }).catch(function (e) { feil(e.message); });
    }

    // Steg 3: kandidater
    function kandidatKort(r, kanVelges) {
      var kort = el("div", "vr-kort");
      var rad = el("div", "vr-velg");
      if (kanVelges) {
        var cb = el("input"); cb.type = "checkbox"; cb.id = "v-" + r.id; cb.checked = !!valgt[r.id];
        cb.addEventListener("change", function () { if (cb.checked) valgt[r.id] = r; else delete valgt[r.id]; lagreValg(); });
        rad.appendChild(cb);
      }
      var tekst = el("div");
      var h = el("h3"); var lab = el("label", null, (r.nr ? r.nr + ". " : "") + r.navn); if (kanVelges) lab.htmlFor = "v-" + r.id; h.appendChild(lab); tekst.appendChild(h);
      tekst.appendChild(el("p", null, r.stilling + (r.firma ? " · " + r.firma : r.avdeling ? " · " + r.avdeling : "")));
      if (r.status === "utilgjengelig") { tekst.appendChild(el("p", null, "Utilgjengelig på datoen (" + (r.fravaerstype || "ukjent") + ").")); rad.appendChild(tekst); kort.appendChild(rad); return kort; }
      tekst.appendChild(el("p", null, "Timepris uten tillegg: " + kr(r.timepris_uten_tillegg) + " (" + r.prisgrunnlag + ")"));
      if (r.type === "egen") {
        tekst.appendChild(el("p", null, "Kompetanse: " + r.kompetanse.join(", ") + " · Vakter på stasjonen siste 12 mnd: " + r.vakter_paa_stasjonen_siste_12_mnd));
      } else {
        tekst.appendChild(el("p", null, r.kategori + " · Avtale " + r.avtale));
        tekst.appendChild(el("p", null, r.merknad));
      }
      rad.appendChild(tekst); kort.appendChild(rad);
      return kort;
    }
    function visKandidater() {
      feil("");
      return hent("get_staffing_candidates", { stasjon: vakt.stasjon, dato: vakt.dato, start: vakt.start, slutt: vakt.slutt }).then(function (k) {
        kand = k;
        // Hent tidligere avkrysninger for samme vakt fra nettleseren.
        var lagretValg = (lesLager().valg || {})[vaktNokkel()] || [];
        valgt = {};
        k.egne.concat(k.innleide).forEach(function (r) { if (lagretValg.indexOf(r.id) >= 0) valgt[r.id] = r; });
        $("sortering").textContent = k.sortering + " " + k.merknad_pris;
        var l = $("kand-liste"); l.textContent = "";
        l.appendChild(el("h3", "vr-gruppe", "Egne ansatte (" + k.antall_egne + ")"));
        if (!k.egne.length) l.appendChild(el("p", "af-empty", "Ingen egne ansatte har alle kravene gyldige på datoen."));
        k.egne.forEach(function (r) { l.appendChild(kandidatKort(r, true)); });
        l.appendChild(el("h3", "vr-gruppe", "Innleide (" + k.antall_innleide + ")"));
        if (!k.innleide.length) l.appendChild(el("p", "af-empty", "Ingen aktive innleide avtaler på datoen."));
        k.innleide.forEach(function (r) { l.appendChild(kandidatKort(r, true)); });
        if (k.utilgjengelige.length) {
          l.appendChild(el("h3", "vr-gruppe", "Utilgjengelige (" + k.antall_utilgjengelige + ")"));
          k.utilgjengelige.forEach(function (r) { l.appendChild(kandidatKort(r, false)); });
        }
        gaa("kandidater");
      }).catch(function (e) { feil(e.message); });
    }

    // Steg 4: kontroll og KI-sammenligning
    function valgteIds() { return kand ? kand.egne.concat(kand.innleide).filter(function (r) { return valgt[r.id]; }).map(function (r) { return r.id; }) : []; }
    function visKontroll() {
      feil("");
      var ids = valgteIds();
      if (!ids.length) { feil("Velg minst én kandidat."); return; }
      hent("check_staffing_selection", { stasjon: vakt.stasjon, dato: vakt.dato, start: vakt.start, slutt: vakt.slutt, ids: ids }).then(function (k) {
        var l = $("kontroll-liste"); l.textContent = "";
        k.resultater.forEach(function (r) {
          var p = valgt[r.id], kort = el("div", "vr-kort");
          var h = el("h3", null, p.nr + ". " + p.navn + " ");
          h.appendChild(el("span", "af-badge" + (r.status === "ok" ? " active" : ""), r.status === "ok" ? "Ingen funn" : r.status === "avvik" ? "Avvik" : "Kurs ok, vakter ukjent"));
          kort.appendChild(h);
          var ul = el("ul"); r.funn.forEach(function (f) { ul.appendChild(el("li", null, f)); }); kort.appendChild(ul);
          l.appendChild(kort);
        });
        $("kontroll-merknad").textContent = k.merknad + " Hviletidskrav: " + k.hviletid_krav_timer + " timer.";
        $("sml-tekst").textContent = ""; $("sml-merke").hidden = true;
        gaa("kontroll");
      }).catch(function (e) { feil(e.message); });
    }
    function kiSvarTekst(s) {
      var t = s.tekst;
      if (s.tallkontroll && !s.tallkontroll.ok) t += "\n\nAdvarsel: tall som ikke står i grunnlaget: " + s.tallkontroll.ukjente_tall.join(", ");
      return t;
    }
    function sammenlign() {
      var ids = valgteIds(); if (!ids.length) return;
      $("sammenlign").disabled = true; $("sml-tekst").textContent = "Spør KI …";
      post("/api/vaktrom/ki", { oppgave: "sammenlign", stasjon: vakt.stasjon, dato: vakt.dato, start: vakt.start, slutt: vakt.slutt, ids: ids })
        .then(function (s) { $("sml-tekst").textContent = kiSvarTekst(s); $("sml-merke").hidden = false; })
        .catch(function (e) { $("sml-tekst").textContent = e.message; })
        .then(function () { $("sammenlign").disabled = false; });
    }

    // Steg 5: vurdering og kontakt
    function fornavn(n) { return String(n || "").split(" ")[0]; }
    function lenker(kort, p, melding) {
      var emne = "Forespørsel om vakt " + vakt.dato + " (" + vakt.stasjon + ")";
      var mail = kort.querySelector(".vr-mail"), tel = kort.querySelector(".vr-tel");
      mail.href = "mailto:" + encodeURIComponent(p.epost || "") + "?subject=" + encodeURIComponent(emne) + "&body=" + encodeURIComponent(melding.value);
      if (tel) tel.href = "tel:" + String(p.telefon || "").replace(/[^+0-9]/g, "");
    }
    function kontaktKort(p, lagret) {
      var kort = el("div", "vr-kort");
      kort.appendChild(el("h3", null, p.navn + (p.firma ? " (" + p.firma + ")" : "")));
      kort.appendChild(el("p", null, "E-post: " + (p.epost || "mangler") + " · Telefon: " + (p.telefon || "mangler")));
      if (p.type === "innleid") kort.appendChild(el("p", null, "Kontaktperson hos firmaet: " + (p.kontaktperson_firma || "ikke registrert")));
      var id = "k-" + p.id;
      var g1 = el("div", "af-group"); var l1 = el("label", "af-label", "Egen vurdering"); l1.htmlFor = id + "-vurd";
      var vurd = el("textarea", "af-textarea"); vurd.id = id + "-vurd"; vurd.rows = 3; vurd.value = lagret ? lagret.vurdering : "";
      g1.appendChild(l1); g1.appendChild(vurd); kort.appendChild(g1);
      var g2 = el("div", "af-group"); var l2 = el("label", "af-label", "Melding"); l2.htmlFor = id + "-meld";
      var meld = el("textarea", "af-textarea"); meld.id = id + "-meld"; meld.rows = 6;
      meld.value = lagret ? lagret.melding : "Hei " + fornavn(p.navn) + ",\n\nKan du ta en vakt på " + vakt.stasjon + " " + vakt.dato + " kl. " + vakt.start + "–" + vakt.slutt + "? Gi meg gjerne svar.\n\nHilsen " + vakt.rolle;
      g2.appendChild(l2); g2.appendChild(meld); kort.appendChild(g2);
      var merke = el("span", "af-source suggested", "AI-forslag"); merke.hidden = true; kort.appendChild(merke);
      var status = el("p", "af-save-status");
      var akt = el("div", "af-actions");
      if (kiPaa) {
        var ki = el("button", "af-btn af-btn-secondary", "Lag kontaktutkast med KI"); ki.type = "button";
        ki.addEventListener("click", function () {
          ki.disabled = true; status.textContent = "Spør KI …";
          post("/api/vaktrom/ki", { oppgave: "kontaktutkast", stasjon: vakt.stasjon, dato: vakt.dato, start: vakt.start, slutt: vakt.slutt, id: p.id })
            .then(function (s) {
              meld.value = s.tekst.split("[NAVN]").join(fornavn(p.navn)); merke.hidden = false;
              status.textContent = s.tallkontroll && !s.tallkontroll.ok ? "AI-forslag. Sjekk tallene: " + s.tallkontroll.ukjente_tall.join(", ") : "AI-forslag satt inn. Les og rediger før du sender.";
              lenker(kort, p, meld);
            })
            .catch(function (e) { status.textContent = e.message; })
            .then(function () { ki.disabled = false; });
        });
        akt.appendChild(ki);
      }
      var mail = el("a", "af-btn af-btn-secondary vr-mail", "Åpne e-post"); akt.appendChild(mail);
      if (p.telefon) akt.appendChild(el("a", "af-btn af-btn-secondary vr-tel", "Ring"));
      var lagre = el("button", "af-btn af-btn-primary", "Lagre i nettleseren"); lagre.type = "button";
      lagre.addEventListener("click", function () {
        var d = lesLager(), nokkel = [p.id, vakt.stasjon, vakt.dato, vakt.start].join("|");
        d.utkast = d.utkast.filter(function (u) { return u.nokkel !== nokkel; });
        d.utkast.push({ nokkel: nokkel, id: p.id, navn: p.navn, type: p.type, firma: p.firma || "", epost: p.epost || "", telefon: p.telefon || "",
          kontaktperson_firma: p.kontaktperson_firma || "", stasjon: vakt.stasjon, dato: vakt.dato, start: vakt.start, slutt: vakt.slutt, rolle: vakt.rolle,
          vurdering: vurd.value, melding: meld.value, lagret: new Date().toISOString().slice(0, 16).replace("T", " ") });
        status.textContent = skrivLager(d) ? "Lagret i denne nettleseren. Ingen vakt eller avtale er opprettet." : "Nettleseren tillater ikke lagring her.";
      });
      akt.appendChild(lagre);
      kort.appendChild(akt); kort.appendChild(status);
      meld.addEventListener("input", function () { lenker(kort, p, meld); });
      lenker(kort, p, meld);
      return kort;
    }
    function visKontakt() {
      var l = $("kontakt-liste"); l.textContent = "";
      var ids = valgteIds();
      if (!ids.length) { l.appendChild(el("p", "af-empty", "Ingen kandidater valgt.")); }
      ids.forEach(function (id) { l.appendChild(kontaktKort(valgt[id], null)); });
      gaa("kontakt");
    }

    // Mine kontaktutkast
    function tegnUtkast() {
      var l = $("utkast-liste"); l.textContent = "";
      var d = lesLager();
      if (!d.utkast.length) { l.appendChild(el("p", "af-empty", "Ingen lagrede utkast i denne nettleseren.")); return; }
      d.utkast.slice().reverse().forEach(function (u) {
        var kort = el("div", "vr-kort");
        kort.appendChild(el("h3", null, u.navn + " · " + u.stasjon + " " + u.dato + " " + u.start + "–" + u.slutt));
        kort.appendChild(el("p", null, "Lagret " + u.lagret + ". Vurdering: " + (u.vurdering || "ingen")));
        var akt = el("div", "af-actions");
        var aapne = el("button", "af-btn af-btn-secondary", "Åpne"); aapne.type = "button";
        aapne.addEventListener("click", function () {
          vakt = { rolle: u.rolle, stasjon: u.stasjon, dato: u.dato, start: u.start, slutt: u.slutt };
          sett("vakt-oppsummert", oppsummer(vakt)); if (opt.vedVakt) opt.vedVakt(oppsummer(vakt));
          var liste = $("kontakt-liste"); liste.textContent = "";
          liste.appendChild(kontaktKort(u, u));
          gaa("kontakt");
        });
        var slett = el("button", "af-btn af-btn-secondary", "Slett"); slett.type = "button";
        slett.addEventListener("click", function () {
          var dd = lesLager(); dd.utkast = dd.utkast.filter(function (x) { return x.nokkel !== u.nokkel; }); skrivLager(dd); tegnUtkast();
        });
        akt.appendChild(aapne); akt.appendChild(slett); kort.appendChild(akt);
        l.appendChild(kort);
      });
    }

    // Oppstart
    byggSteg();
    $("stasjon").addEventListener("change", tegnKrav);
    if ($("rolle")) $("rolle").addEventListener("change", sjekkRolle);
    $("til-historikk").addEventListener("click", function () {
      try { feil(""); settVakt(); gaa("historikk"); visHistorikk(); } catch (e) { feil(e.message); }
    });
    $("vis-historikk").addEventListener("click", visHistorikk);
    $("til-kandidater").addEventListener("click", visKandidater);
    $("til-kontroll").addEventListener("click", visKontroll);
    $("sammenlign").addEventListener("click", sammenlign);
    $("til-kontakt").addEventListener("click", visKontakt);

    var param = new URLSearchParams(location.search);
    var iDag = new Date(); iDag.setDate(iDag.getDate() + ((6 - iDag.getDay() + 7) % 7 || 7));
    $("dato").value = iDag.toISOString().slice(0, 10);

    fetch("/api/status").then(function (r) { return r.json(); }).then(function (s) {
      kiPaa = !!s.llm;
      sett("ki-status", kiPaa ? TEKST.kiPa + s.llm_modell + "." : TEKST.kiAv);
      $("sml-blokk").hidden = !kiPaa;
    }).catch(function () { sett("ki-status", TEKST.kiAv); $("sml-blokk").hidden = true; });

    var startSteg = opt.startSteg || (location.hash === "#utkast" ? "kontakt" : "vakt");
    Promise.all([hent("list_stations"), hent("list_roles")]).then(function (svar) {
      stasjoner = svar[0];
      roller = (svar[1].roller || svar[1] || []).map(function (r) { return r.navn; });
      stasjoner.forEach(function (s) { var o = el("option", null, s.stasjon); o.value = s.stasjon; $("stasjon").appendChild(o); });
      if ($("rolle")) {
        roller.forEach(function (n) { var o = el("option", null, n); o.value = n; $("rolle").appendChild(o); });
        if (param.get("rolle") && roller.indexOf(param.get("rolle")) >= 0) $("rolle").value = param.get("rolle");
        else $("rolle").value = roller[0] || "";
      }
      if (param.get("stasjon")) $("stasjon").value = param.get("stasjon");
      tegnKrav(); sjekkRolle();
      gaa(startSteg);
      if (startSteg === "kontakt") $("utkast").focus();
    }).catch(function (e) { feil("Fikk ikke hentet stasjoner og roller: " + e.message); });

    return { gaa: gaa, steg: STEG };
  }
};
