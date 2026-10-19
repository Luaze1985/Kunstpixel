const $ = id => document.getElementById(id);
const s = {
  dataset: localStorage.getItem('kp-dataset') || '',
  workspace: localStorage.getItem('kp-workspace') || 'work',
  week: localStorage.getItem('kp-week') || '',
  activity: localStorage.getItem('kp-activity') || '',
  snapshot: null, proposal: null, candidates: [], sources: {},
  candidateQuery: '', candidateFilter: 'relevant', personPage: 1,
  validation: null
};
const e = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const stamp = v => new Date(v).toLocaleString('nb-NO', {weekday:'short', day:'numeric', month:'short', hour:'2-digit', minute:'2-digit'});

async function api(url, body) {
  const reset = url.endsWith('/reset');
  if (s.dataset && !url.startsWith('/api/planning/datasets')) {
    url += `${url.includes('?') ? '&' : '?'}dataset_version=${encodeURIComponent(s.dataset)}`;
  }
  const options = body === undefined ? {} : {
    method: 'POST', headers: {'Content-Type':'application/json', ...(reset ? {'X-Kunstpixel-Action':'demo-reset'} : {})},
    body: JSON.stringify({...body, dataset_version:s.dataset || null})
  };
  const response = await fetch(url, options);
  const result = await response.json();
  if (!response.ok) throw Error(result.message || result.detail || `HTTP ${response.status}`);
  return result;
}
function notice(message) {
  $('notice').textContent = message;
  $('notice').style.display = 'block';
  clearTimeout(notice.timer);
  notice.timer = setTimeout(() => $('notice').style.display = 'none', 5500);
}
function sourceList(ids) {
  return `<ul class="source">${[...new Set(ids || [])].map(id => {
    const src = s.sources[id];
    return src ? `<li><a href="${e(src.url)}" target="_blank" rel="noopener">${e(id)} · ${e(src.title)}</a></li>`
      : `<li>${e(id)} · fiktivt prosjektgrunnlag</li>`;
  }).join('')}</ul>`;
}
async function refreshDatasets() {
  const info = await api('/api/planning/datasets');
  if (!info.versions.includes(s.dataset)) s.dataset = info.active_version;
  $('dataset').innerHTML = info.versions.map(v => `<option value="${e(v)}">${e(v)}</option>`).join('');
  $('dataset').value = s.dataset;
  $('dataset-state').textContent = `Aktiv versjon: ${info.active_version}. Tidligere versjoner kan åpnes uten å miste beslutninger.`;
  localStorage.setItem('kp-dataset', s.dataset);
}
async function loadPeople() {
  const query = encodeURIComponent($('person-search').value);
  const status = $('person-status').value;
  const data = await api(`/api/planning/people?query=${query}&status=${status}&page=${s.personPage}&week_start=${encodeURIComponent(s.week)}`);
  $('people').innerHTML = data.people.map(p => `<div class="person"><strong>${e(p.name)} · ${e(p.id)}</strong>
    <p>${e(p.title)} · ${e(p.department)} · ${p.active ? 'Aktiv' : 'Historikk'}</p>
    <p class="muted">Kompetanse: ${e(p.skills.join(', ') || 'ikke kartlagt')} ·
    Opplæring: ${e(Object.keys(p.training).join(', ') || 'ukjent')}</p>
    <p class="muted">Kilder: ${e(p.field_sources.employment)}; ${e(p.field_sources.skills)};
    ${e(p.field_sources.availability)}</p></div>`).join('') || '<p>Ingen treff.</p>';
  $('people-page').textContent = `Side ${data.page} · ${data.total} treff`;
  $('people-prev').disabled = s.personPage <= 1;
  $('people-next').disabled = s.personPage * 20 >= data.total;
}
async function load() {
  try {
    s.snapshot = await api(`/api/planning/weeks/${encodeURIComponent(s.week)}?workspace=${encodeURIComponent(s.workspace)}`);
    const latest = await api(`/api/planning/proposals/latest?workspace=${encodeURIComponent(s.workspace)}&week_start=${encodeURIComponent(s.week)}`);
    s.proposal = latest.proposal === null || latest.base_version !== s.snapshot.version ? null : latest;
    if (!s.snapshot.activities.some(a => a.id === s.activity)) s.activity = s.snapshot.activities[0]?.id || '';
    localStorage.setItem('kp-workspace', s.workspace);
    localStorage.setItem('kp-week', s.week);
    localStorage.setItem('kp-activity', s.activity);
    $('reset').hidden = !s.workspace.startsWith('demo:');
    renderOverview();
    await renderDemoInfo();
    await select(s.activity);
    renderProposal();
    await loadPeople();
  } catch (err) { notice(err.message); }
}
function renderOverview() {
  const v = s.snapshot;
  $('version').textContent = `Planversjon ${v.version} · ${e(v.context_version)}`;
  $('summary').innerHTML = `<div class="stats"><div class="stat"><strong>${v.activities.length}</strong>oppgaver</div>
    <div class="stat"><strong>${v.activities.filter(a => a.kind === 'event').length}</strong>arrangementer</div>
    <div class="stat"><strong>${v.checks.uncovered_count}</strong>udekkede poster</div></div>
    <p class="next"><strong>Neste handling:</strong> ${e(v.next_action)}</p>
    <p class="muted">${v.checks.unresolved.length} uavklarte kontroller</p>`;
  $('activities').innerHTML = v.activities.map(a => `<button class="activity ${a.id === s.activity ? 'active' : ''}" data-activity="${e(a.id)}">
    <span><strong>${e(a.title)}</strong><br><small>${stamp(a.starts_at)} · ${a.kind === 'event' ? 'Arrangement' : 'Fast oppgave'}</small></span>
    <span class="badge ${a.status === 'udekket' ? 'warn' : ''}">${e(a.status)}</span></button>`).join('');
  document.querySelectorAll('[data-activity]').forEach(b => b.onclick = () => select(b.dataset.activity));
}
async function renderDemoInfo() {
  if (!s.workspace.startsWith('demo:')) { $('demo-info').innerHTML = ''; return; }
  const id = s.workspace.split(':')[1];
  const data = await api(`/api/planning/demo/scenarios/${id}`);
  $('demo-info').innerHTML = `<div class="checks"><strong>Testscenario ${e(id)}: ${e(data.title)}</strong>
    <p>${e(data.description)}</p><p class="muted">${e(data.week_mapping)}</p></div>`;
}
async function select(id) {
  if (!id) return;
  s.activity = id;
  localStorage.setItem('kp-activity', id);
  document.querySelectorAll('[data-activity]').forEach(b => b.classList.toggle('active', b.dataset.activity === id));
  const activity = s.snapshot.activities.find(a => a.id === id);
  $('detail-title').textContent = activity.title;
  try {
    s.candidates = (await api(`/api/planning/activities/${encodeURIComponent(id)}/candidates?workspace=${encodeURIComponent(s.workspace)}`)).candidates;
    renderDetail(activity);
  } catch (err) { notice(err.message); }
}
function renderDetail(a) {
  const assigned = s.snapshot.assignments.filter(x => x.activity_id === a.id);
  $('detail').innerHTML = `<p><strong>${stamp(a.starts_at)}–${new Date(a.ends_at).toLocaleTimeString('nb-NO',{hour:'2-digit',minute:'2-digit'})}</strong></p>
    <p class="muted">Arbeidstid inkl. klargjøring: ${stamp(a.work_start)}–${stamp(a.work_end)}</p>
    <p><strong>Behov:</strong> ${Object.entries(a.requirements).map(([k,n]) => `${e(k)} × ${n}`).join(', ')}</p>
    <p class="next"><strong>Neste handling:</strong> ${e(a.next_action)}</p>
    <h3>Tildelte</h3><p>${assigned.length ? assigned.map(x => `${e(s.candidates.find(c => c.person_id === x.person_id)?.name || x.person_id)} (${e(x.skill)})`).join(', ') : 'Ingen tildelt'}</p>
    <h3>Kandidater, kompetanse og kontakt</h3>
    <input id="candidate-search" type="search" placeholder="Søk kandidat"><label>Vis <select id="candidate-filter">
      <option value="relevant">Relevant kompetanse</option><option value="eligible">Kan foreslås</option><option value="all">Alle</option>
    </select></label><div id="candidate-list"></div><h3>Kilder for oppgaven</h3>${sourceList(a.source_ids)}`;
  $('candidate-search').value = s.candidateQuery;
  $('candidate-filter').value = s.candidateFilter;
  $('candidate-search').oninput = ev => { s.candidateQuery = ev.target.value; renderCandidateList(a); };
  $('candidate-filter').onchange = ev => { s.candidateFilter = ev.target.value; renderCandidateList(a); };
  renderCandidateList(a);
}
function renderCandidateList(a) {
  const query = s.candidateQuery.toLocaleLowerCase('nb-NO');
  const matches = s.candidates.filter(c =>
    (s.candidateFilter === 'all' || s.candidateFilter === 'eligible' && c.eligible || s.candidateFilter === 'relevant' && c.has_skill)
    && `${c.name} ${c.person_id} ${c.skill}`.toLocaleLowerCase('nb-NO').includes(query));
  matches.sort((a,b) => Number(b.eligible) - Number(a.eligible) || a.name.localeCompare(b.name,'nb-NO'));
  $('candidate-list').innerHTML = `<p class="muted">${matches.length} treff · viser maks 20. Bruk søk for flere.</p>` +
    (matches.slice(0,20).map(c => `<div class="person ${c.eligible ? 'eligible' : 'blocked'}">
      <strong>${e(c.name)} · ${e(c.person_id)} · ${e(c.skill)}</strong><p>${e(c.reason)}</p>
      <p class="muted">${e(c.title || '')} · Opplæring: ${c.training === true ? 'ja' : 'ukjent'} ·
      Ledig ukekapasitet: ${e(c.available_hours)} t · Kontakt: ${e(c.contact_status)}</p>
      <p class="muted">Kilde: ${e(c.field_sources?.employment || 'fiktivt scenario')};
      ${e(c.field_sources?.skills || '')}; ${e(c.field_sources?.availability || '')}</p>
      <label>Status <select data-contact="${e(c.person_id)}"><option value="ikke_kontaktet">Ikke kontaktet</option>
      <option value="forespurt">Forespurt</option><option value="ja">Ja</option><option value="nei">Nei</option>
      <option value="trukket">Trukket</option></select></label>
      <button data-save="${e(c.person_id)}" ${c.active ? '' : 'disabled'}>Lagre kontakt</button>${sourceList(c.source_ids)}</div>`).join('') || '<p>Ingen kandidater i dette filteret.</p>');
  document.querySelectorAll('[data-contact]').forEach(el => el.value = s.candidates.find(c => c.person_id === el.dataset.contact).contact_status);
  document.querySelectorAll('[data-save]').forEach(button => button.onclick = () => saveContact(a.id, button.dataset.save));
}
async function saveContact(activity_id, person_id) {
  try {
    const status = document.querySelector(`[data-contact="${person_id}"]`).value;
    await api('/api/planning/contacts', {workspace:s.workspace, activity_id, person_id, status, expected_version:s.snapshot.version});
    await load(); notice('Kontaktstatus lagret. Hele ukeplanen er kontrollert på nytt.');
  } catch (err) { notice(err.message); }
}
function renderProposal() {
  const p = s.proposal;
  if (!p) { $('proposal').innerHTML = '<p>Ingen forslag laget for denne planversjonen.</p>'; return; }
  const decided = Object.keys(p.decisions || {}).length;
  $('proposal').innerHTML = `<p><strong>${e(p.rationale)}</strong></p>
    <p class="muted">${e(p.source)} · grunnlag ${e(p.context_version)} · planversjon ${p.base_version}</p>
    ${p.model ? `<p class="muted">Modell: ${e(p.model)} · inndata ${e(p.usage?.input_tokens ?? 'ukjent')} tokens · utdata ${e(p.usage?.output_tokens ?? 'ukjent')} tokens</p>` : ''}
    <div class="checks"><strong>Gjeldende plan:</strong> ${s.snapshot.checks.uncovered_count} udekkede poster;
    ${s.snapshot.checks.unresolved.length} uavklarte kontroller.
    ${decided ? '<p>Forslaget er delvis behandlet. Lag nytt forslag for oppdatert helhetskontroll.</p>' :
      `<p>Hvis hele forslaget vedtas: ${p.review.uncovered_count} udekkede poster;
      ${p.review.unresolved.length} uavklarte kontroller.</p>`}
    <p>Manglende informasjon:</p><ul>${p.missing_information.map(x => `<li>${e(x)}</li>`).join('') || '<li>Ingen oppgitt</li>'}</ul>
    ${sourceList(p.source_ids)}</div><h3>Endringer fra gjeldende plan</h3>
    ${p.changes.map(c => { const d = p.decisions?.[c.fact_id]; return `<div class="change">
      <strong>${e(c.action === 'remove' ? 'Fjern' : 'Tildel')} ${e(c.activity_id)} · ${e(c.skill)} → ${e(c.person_id)}</strong>
      <p>${e(c.reason)}</p>${sourceList(c.source_ids)}
      ${d ? `<p>Beslutning: ${e(d.decision)} · ${e(d.rationale)}</p>` :
        `<button data-fact="${e(c.fact_id)}" data-decision="approved">Godkjenn</button>
         <button class="reject" data-fact="${e(c.fact_id)}" data-decision="rejected">Avvis</button>`}</div>`;
    }).join('') || '<p>Ingen endringer foreslått.</p>'}`;
  document.querySelectorAll('[data-decision]').forEach(b => b.onclick = () => decide(b.dataset.fact, b.dataset.decision));
}
async function decide(fact_id, decision) {
  try {
    await api(`/api/planning/proposals/${s.proposal.id}/decisions`, {
      workspace:s.workspace, fact_id, decision,
      rationale:decision === 'approved' ? 'Godkjent i øvelsen' : 'Avvist i øvelsen',
      expected_version:s.snapshot.version
    });
    await load(); notice('Beslutning lagret. Hele planen er kontrollert på nytt.');
  } catch (err) { notice(err.message); }
}
async function modelStatus() {
  try {
    const model = await api('/api/planning/model');
    $('generate-ai').disabled = !model.configured;
    $('model-state').textContent = model.configured ? `OpenAI klar: ${model.model}. Kun kortlistede kandidater sendes.`
      : 'OpenAI er ikke konfigurert. Lokalt forslag kan brukes uten API-kall.';
  } catch (err) { $('model-state').textContent = 'Kunne ikke lese KI-oppsett.'; }
}
async function init() {
  try {
    const [weeks, sources, quality] = await Promise.all([
      api('/api/planning/weeks'), api('/api/planning/sources'), api('/api/planning/data-quality')
    ]);
    s.sources = Object.fromEntries(sources.sources.map(x => [x.id,x]));
    $('quality').innerHTML = `<p>${quality.shifts} syntetiske vakter kontrollert. ${quality.person_days_over_24_hours}
      persondager over 24 timer; ${quality.person_days_over_13_hours} over 13 timer.
      <strong>Historiske vakter brukes ikke i forslag.</strong></p><p class="muted">${e(quality.reason)}</p>`;
    await refreshDatasets();
    $('week').innerHTML = weeks.weeks.map(w => `<option value="${e(w)}">${e(w)}</option>`).join('');
    if (!weeks.weeks.includes(s.week)) s.week = weeks.weeks[0];
    $('week').value = s.week;
    $('workspace').value = s.workspace;
    await load(); await modelStatus();
  } catch (err) { notice(err.message); }
}
$('workspace').onchange = async ev => { s.workspace = ev.target.value; s.proposal = null; await load(); };
$('week').onchange = async ev => { s.week = ev.target.value; s.proposal = null; await load(); };
$('dataset').onchange = async ev => { s.dataset = ev.target.value; s.proposal = null; localStorage.setItem('kp-dataset',s.dataset); await load(); };
$('person-search').oninput = () => { s.personPage = 1; loadPeople().catch(err => notice(err.message)); };
$('person-status').onchange = () => { s.personPage = 1; loadPeople().catch(err => notice(err.message)); };
$('people-prev').onclick = () => { s.personPage--; loadPeople().catch(err => notice(err.message)); };
$('people-next').onclick = () => { s.personPage++; loadPeople().catch(err => notice(err.message)); };
$('validate-data').onclick = async () => {
  try {
    s.validation = await api('/api/planning/datasets/validate', {});
    $('validation').innerHTML = s.validation.valid
      ? `<p class="next">${s.validation.changed_people === 0 ? 'Ingen endringer i arbeidskopien.' :
          `${s.validation.changed_people} personer endres. Ny versjon: ${e(s.validation.version)}. Gjeldende beslutninger beholdes i forrige versjon.`}</p><p>Udekkede poster i grunnplanen:
         ${s.validation.baseline_impact.map(x => `${e(x.week_start)}: ${x.uncovered_before} → ${x.uncovered_after}`).join(' · ')}</p>`
      : `<p class="next">Kan ikke aktiveres:</p><ul>${s.validation.errors.map(x => `<li>${e(x)}</li>`).join('')}</ul>`;
    $('activate-data').disabled = !s.validation.valid || s.validation.changed_people === 0;
  } catch (err) { notice(err.message); }
};
$('activate-data').onclick = async () => {
  try {
    if (!s.validation?.valid) return;
    const result = await api('/api/planning/datasets/activate', {expected_checksum:s.validation.checksum});
    s.dataset = result.active_version; s.validation = null;
    $('activate-data').disabled = true;
    await refreshDatasets(); await load();
    notice('Nytt datagrunnlag aktivert. Tidligere status ligger i forrige versjon.');
  } catch (err) { notice(err.message); }
};
$('generate').onclick = async () => {
  try { s.proposal = await api('/api/planning/proposals', {workspace:s.workspace, week_start:s.week, source:'simulated'});
    renderProposal(); notice('Lokalt forslag laget. Gjeldende plan er uendret.'); }
  catch (err) { notice(err.message); }
};
$('generate-ai').onclick = async () => {
  const button = $('generate-ai'); button.disabled = true;
  try { s.proposal = await api('/api/planning/proposals', {workspace:s.workspace, week_start:s.week, source:'openai'});
    renderProposal(); notice('KI-forslag kontrollert. Gjeldende plan er uendret.'); }
  catch (err) { notice(err.message); } finally { await modelStatus(); }
};
$('reset').onclick = async () => {
  try { await api(`/api/planning/demo/scenarios/${s.workspace.split(':')[1]}/reset`, {});
    await load(); notice('Valgt demo er nullstilt.'); }
  catch (err) { notice(err.message); }
};
init();
