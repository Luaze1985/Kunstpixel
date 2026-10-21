(() => {
  'use strict';
  const el = id => document.getElementById(id);
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const labels = {synthetic_report:'Konstruert demosvar',reported:'Konstruert demosvar',assumed:'Antatt',unknown:'Ukjent',not_applicable:'Ikke relevant',active:'Aktiv',historical:'Historisk',future:'Fremtidig',daily:'Daglig',weekly:'Ukentlig',monthly:'Månedlig',rarely:'Sjelden',never:'Aldri'};
  const label = v => labels[v] || v || 'Ikke registrert';
  const list = v => Array.isArray(v) ? v.join(', ') || 'Ikke registrert' : v || 'Ikke registrert';
  let page = 1, generation = 0, detailGeneration = 0, selected = null, timer;
  async function request(url, body) {
    const r = await fetch(url, body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const d = await r.json();
    if (!r.ok) throw new Error(typeof d.detail === 'string' ? d.detail : d.message || `Forespørselen mislyktes (${r.status}).`);
    return d;
  }
  function params() { return new URLSearchParams({query:el('ai-query').value,department:el('ai-department').value,status:el('ai-status').value,tool:el('ai-tool').value,page:String(page),page_size:'20'}); }
  function options(id, rows, name, value) {
    const field = el(id), current = field.value;
    field.innerHTML = `<option value="">${esc(name)}</option>` + rows.map(row => `<option value="${esc(value(row))}">${esc(typeof row === 'string' ? row : row.name)}</option>`).join('');
    field.value = current;
  }
  function showSummary(d) {
    const c = d.counts, a = d.averages;
    el('ai-summary').innerHTML = `<div class="ai-stats"><div><strong>${esc(c.total)}</strong>personer i utvalget</div><div><strong>${esc(c.reported)}</strong>konstruerte demosvar · ${esc(c.assumed)} antatt</div><div><strong>${esc(c.unknown)}</strong>ukjent · ${esc(c.not_applicable)} ikke relevant</div><div><strong>${esc(a.competence ?? '–')} / 5</strong>kompetanse · ${esc(a.competence_count)} av ${esc(c.total)} personer</div><div><strong>${esc(a.maturity ?? '–')} / 5</strong>modenhet · ${esc(a.maturity_count)} av ${esc(c.total)} personer</div></div><p class="ai-note">${esc(c.active)} aktive, ${esc(c.historical)} historiske og ${esc(c.future ?? 0)} fremtidige. Gjennomsnitt bruker bare kjente skårer. Ansettelsesstatus er et filter, ikke en forklaring på KI-bruk.</p><details><summary>Avdelingsgrunnlag og antakelser</summary>${d.departments.map(x => `<p><strong>${esc(x.name)}</strong> · ${esc(x.description)}<br>${esc(list(x.assumptions))}<br>Kilde: ${esc(x.source)}</p>`).join('')}<p>Referansedato: ${esc(d.metadata.reference_date)} · Versjon: ${esc(d.metadata.version)}<br>${esc(list(d.metadata.limitations))}</p></details>`;
  }
  async function load() {
    const token = ++generation;
    el('ai-message').textContent = 'Henter ansatte …';
    el('ai-people').setAttribute('aria-busy','true');
    el('ai-prev').disabled = el('ai-next').disabled = true;
    try {
      const q = params(), [d, summary] = await Promise.all([request(`/api/ai/people?${q}`),request(`/api/ai/summary?${q}`)]);
      if (token !== generation) return;
      showSummary(summary);
      el('ai-people').innerHTML = d.people.map(p => `<button class="ai-person" data-person="${esc(p.person_id)}"><strong>${esc(p.name)}</strong><span>${esc(p.person_id)} · ${esc(p.title)}</span><span>${esc(p.department)} · ${esc(label(p.employment_status))}</span><span class="ai-chip">${esc(label(p.knowledge_status))}</span><span>${esc(label(p.frequency))} · ${esc(list(p.tools))}</span></button>`).join('') || '<p class="ai-empty">Ingen ansatte passer søket. Prøv færre filtre.</p>';
      el('ai-page').textContent = `Side ${d.page} · ${d.total} treff`;
      el('ai-prev').disabled = page <= 1;
      el('ai-next').disabled = page * d.page_size >= d.total;
      el('ai-message').textContent = `${d.total} treff. Alle personopplysninger og KI-observasjoner er syntetiske.`;
    } catch (err) { if (token === generation) el('ai-message').textContent = err.message; }
    finally { if (token === generation) el('ai-people').removeAttribute('aria-busy'); }
  }
  function facts(rows) { return `<dl class="ai-facts">${rows.map(([k,v]) => `<dt>${esc(k)}</dt><dd>${esc(v ?? 'Ikke registrert')}</dd>`).join('')}</dl>`; }
  function scoreOptions(v) { return '<option value="">Ikke registrert</option>' + [1,2,3,4,5].map(n => `<option value="${n}" ${v === n ? 'selected' : ''}>${n}</option>`).join(''); }
  async function openPerson(id, focus = true) {
    const token = ++detailGeneration;
    selected = id;
    el('ai-detail').setAttribute('aria-busy','true');
    try {
      const p = await request(`/api/ai/people/${encodeURIComponent(id)}`);
      if (token !== detailGeneration) return;
      const h = p.hr_context, original = p.original_profile || p;
      el('ai-detail').innerHTML = `<p class="eyebrow">Syntetisk personprofil</p><h3 id="ai-detail-heading" tabindex="-1">${esc(p.name)}</h3>${facts([['Person-ID',p.person_id],['Stilling',`${p.title} · ${p.position_percent ?? '–'} %`],['Avdeling',p.department],['Ansettelse',label(p.employment_status)],['Kunnskapsstatus',label(p.knowledge_status)],['Individuell supplering',p.observation_status === 'supplemental' ? 'Ja, se revisjonshistorikk' : 'Ingen'],['KI-bruk',label(p.frequency)],['Verktøy',list(p.tools)],['Oppgaver',list(p.task_types)],['Kompetanse',p.competence == null ? 'Ikke registrert' : `${p.competence} / 5`],['Modenhet',p.maturity == null ? 'Ikke registrert' : `${p.maturity} / 5`],['Dato for opprinnelig KI-bruk',original.observation_date],['Kilde for opprinnelig KI-bruk',original.source],['Nyeste supplering – kilde',p.observation_status === 'supplemental' ? p.source : 'Ingen supplering'],['Nyeste supplering – dato',p.supplemental_date || 'Ingen supplering'],['Metode for opprinnelig grunnlag',original.method],['Datatype',p.synthetic ? 'Syntetisk' : 'Ikke angitt'],['Revisjon',p.revision]])}<p class="ai-description">${esc(p.description || 'Ingen individuell beskrivelse registrert.')}</p><details class="ai-original"><summary>Opprinnelig grunnlag</summary>${facts([['Kilde',original.source],['Dato',original.observation_date],['Periode fra',original.period_start],['Periode til',original.period_end],['Kompetanse',original.competence == null ? 'Ikke registrert' : `${original.competence} / 5`],['Modenhet',original.maturity == null ? 'Ikke registrert' : `${original.maturity} / 5`],['Grunnlag',list(original.basis)],['Usikkerhet',original.uncertainty]])}<p class="ai-description">${esc(original.description)}</p></details><h4>HR-kontekst</h4>${h ? facts([['Periode',`${h.period_from} – ${h.period_to}`],['Vakter',h.shift_count],['Vakttimer',h.shift_hours],['Fravær, kalenderdager',h.absence_days],['Kilde',h.source]]) : '<p>Ingen HR-kontekst tilgjengelig.</p>'}<p class="ai-note">Fravær er kalenderdager i kilden, ikke sykefraværsprosent. HR-kontekst brukes ikke til å utlede KI-kompetanse eller modenhet.</p><h4>Suppler individuell observasjon</h4><p class="ai-note">Registreringen er syntetisk og endrer ikke bemanningsplan eller kvalifikasjoner. Kompetanse: 1 nybegynner, 3 selvstendig grunnbruk, 5 veileder andre. Modenhet: 1 utforsking, 3 gjentatt arbeidsmåte, 5 systematisk forbedring. La feltet stå tomt ved ukjent.</p><form id="ai-observation"><label for="ai-description">Individuell beskrivelse</label><textarea id="ai-description" required maxlength="4000" rows="4">${esc(p.description || '')}</textarea><label for="ai-source">Kilde eller grunnlag</label><input id="ai-source" required maxlength="500" value=""><div class="ai-score-fields"><label>Kompetanse<select id="ai-competence">${scoreOptions(p.competence)}</select></label><label>Modenhet<select id="ai-maturity">${scoreOptions(p.maturity)}</select></label></div><button type="submit">Lagre syntetisk observasjon</button><p id="ai-save-message" role="status" aria-live="polite"></p></form><h4>Revisjonshistorikk</h4><div class="ai-history">${(p.history || []).map(r => `<article><strong>Revisjon ${esc(r.revision)} · ${esc(r.observation_date || r.recorded_at || r.created_at || '')}</strong><p>${esc(r.description)}</p><p>Kilde: ${esc(r.source)} · Kompetanse: ${esc(r.competence ?? 'Ukjent')} · Modenhet: ${esc(r.maturity ?? 'Ukjent')}</p></article>`).join('') || '<p>Ingen tidligere suppleringer.</p>'}</div>`;
      el('ai-observation').addEventListener('submit', async ev => {
        ev.preventDefault();
        const button = ev.currentTarget.querySelector('button');
        button.disabled = true;
        el('ai-save-message').textContent = 'Lagrer …';
        const body = {expected_revision:p.revision,description:el('ai-description').value,source:el('ai-source').value,competence:el('ai-competence').value ? Number(el('ai-competence').value) : null,maturity:el('ai-maturity').value ? Number(el('ai-maturity').value) : null};
        try {
          await request(`/api/ai/people/${encodeURIComponent(id)}/observations`,body);
          if (selected !== id || token !== detailGeneration) return;
          await openPerson(id,false);
          el('ai-save-message').textContent = 'Observasjonen er lagret. Historikken er oppdatert.';
          load();
        } catch (err) { if (selected === id && token === detailGeneration) { el('ai-save-message').textContent = `${err.message} Ved revisjonskonflikt: åpne personkortet på nytt før du prøver igjen.`; button.disabled = false; } }
      });
      if (focus) el('ai-detail-heading').focus();
    } catch (err) { if (token === detailGeneration) el('ai-message').textContent = err.message; }
    finally { if (token === detailGeneration) el('ai-detail').removeAttribute('aria-busy'); }
  }
  function tab(planning) {
    el('planning-view').hidden = !planning;
    el('planning-selectors').hidden = !planning;
    el('ai-view').hidden = planning;
    el('planning-tab').toggleAttribute('aria-current',planning);
    el('ai-tab').toggleAttribute('aria-current',!planning);
    (planning ? el('planning-tab') : el('ai-tab')).setAttribute('aria-current','page');
  }
  el('ai-tab').onclick = () => tab(false);
  el('planning-tab').onclick = () => tab(true);
  el('ai-filters').onsubmit = ev => { ev.preventDefault(); clearTimeout(timer); page = 1; load(); };
  ['ai-department','ai-status','ai-tool'].forEach(id => el(id).onchange = () => { page = 1; load(); });
  el('ai-query').oninput = () => { clearTimeout(timer); ++generation; timer = setTimeout(() => { page = 1; load(); },250); };
  el('ai-prev').onclick = () => { page--; load(); };
  el('ai-next').onclick = () => { page++; load(); };
  el('ai-people').onclick = ev => { const b = ev.target.closest('[data-person]'); if (b) openPerson(b.dataset.person); };
  request('/api/ai/summary').then(d => { options('ai-department',d.departments,'Alle avdelinger',r => r.id); options('ai-tool',d.tools,'Alle verktøy',r => r); load(); }).catch(err => { el('ai-message').textContent = err.message; });
})();
