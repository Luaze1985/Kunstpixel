"""Versjonert, reproduserbart KI-demogrunnlag; ingen database eller personvurderingstjeneste."""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[3] / '05_data' / 'hr_simulator'
REFERENCE_DATE = '2026-10-21'
METHOD = 'ki-demo-v1: SHA256(ansatt_id), rolle-/oppgavemal og avdelingsscenario; ingen demografi'
SOURCE = '05_data/hr_simulator/staff_source.csv'
AI_START = '2023-01-01'

# Dette er konstruerte avdelingsscenarioer, ikke observerte avdelingsmålinger.
DEPARTMENT_SCENARIOS = {
    'Ledelse': ('ledelse', 0.75, ['ChatGPT', 'Microsoft Copilot'], ['møteforberedelse', 'rapportutkast', 'rutineutkast'],
                'Administrative tekster og møtearbeid gir mulige bruksområder.'),
    'Kuratering': ('kuratering', 0.65, ['ChatGPT', 'Claude'], ['idéutvikling', 'tekstutkast', 'språkstøtte'],
                   'Utkast og språkstøtte kan brukes; kunstfaglige påstander må kontrolleres.'),
    'Samling': ('samling', 0.45, ['Microsoft Copilot', 'ChatGPT'], ['metadatastøtte', 'dokumentasjonsutkast', 'språkstøtte'],
                'Digital dokumentasjon er mulig; fysisk konservering erstattes ikke av KI.'),
    'Formidling': ('formidling', 0.55, ['ChatGPT', 'Microsoft Copilot'], ['formidlingsutkast', 'tilpasning av språk', 'idéutvikling'],
                   'Forberedelse kan støttes av KI; publikumsarbeidet er fortsatt menneskelig.'),
    'Drift': ('drift', 0.30, ['Microsoft Copilot', 'ChatGPT'], ['sjekklisteutkast', 'rutineutkast', 'oppsummering'],
              'Rutiner kan støttes; vakthold, servering og tekniske kontroller krever faglig utføring.'),
    'Marked': ('marked', 0.85, ['ChatGPT', 'Adobe Firefly', 'Microsoft Copilot'], ['kampanjeutkast', 'innholdsideer', 'språkstøtte'],
                'Digitale innholdsoppgaver gir flere mulige bruksflater; publisering krever kontroll.'),
}


def load_dataset(path: Path | None = None) -> dict:
    """Les et publisert JSON-datasett. Returner et nytt objekt for hver innlasting."""
    with (path or DATA_DIR / 'ai_profiles.json').open(encoding='utf-8') as handle:
        return json.load(handle)


def generate_dataset(rows: list[dict[str, str]]) -> dict:
    """Generer scenarioer med stabil ID-seed, uavhengig av radrekkefølge og andre personer."""
    ids = [r['ansatt_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Ansatt-ID må være unik')
    departments = []
    for name in sorted({r['avdeling'] for r in rows}):
        code, _, _, _, description = DEPARTMENT_SCENARIOS[name]
        departments.append({
            'id': code, 'name': name, 'description': description,
            'assumptions': ['Syntetisk avdelingsscenario, ikke målt bruk.',
                            'Rolle og oppgaver gir bare et antakelsesgrunnlag for individer.'],
            'source': 'Konstruert demoscenario v1; avdelingsnavn fra ' + SOURCE,
        })
    return {
        'metadata': {
            'version': '1.0', 'reference_date': REFERENCE_DATE, 'synthetic': True,
            'method': METHOD, 'source': SOURCE,
            'modern_ai_start': AI_START,
            'scales': {
                'competence': {'1': 'Nybegynner, trenger veiledning', '2': 'Enkel bruk med støtte',
                               '3': 'Selvstendig grunnbruk og kontroll', '4': 'Avansert bruk og kildekritikk',
                               '5': 'Veileder andre og vurderer begrensninger'},
                'maturity': {'1': 'Utforsking', '2': 'Enkeltstående forsøk', '3': 'Gjentatt arbeidsmåte',
                             '4': 'Avklarte rutiner og kontroll', '5': 'Systematisk forbedring og oppfølging'},
            },
            'limitations': ['Alle svar og skårer er konstruerte, også synthetic_report.',
                            'Ingen effekt på arbeidsinnsats, kvalitet eller fravær er målt.',
                            'Historiske profiler beskriver en historisk periode, ikke nåværende bruk.',
                            'Ukjent svar er adskilt fra aldri-bruk.'],
        },
        'departments': departments,
        'profiles': [_profile(r) for r in sorted(rows, key=lambda r: r['ansatt_id'])],
    }


def _profile(row: dict[str, str]) -> dict:
    pid = row['ansatt_id']
    rng = random.Random(int(hashlib.sha256(('ki-demo-v1:' + pid).encode()).hexdigest(), 16))
    start, end = row['ansatt_fra'], row['ansatt_til'] or REFERENCE_DATE
    if start > end:
        # Åpen fremtidig ansettelse har ikke sluttdato ved referansedatoen.
        if row['ansatt_til']:
            raise ValueError('Ansettelsesperioden er ugyldig: ' + pid)
    status = 'future' if start > REFERENCE_DATE else 'historical' if end < REFERENCE_DATE else 'active'
    dept, propensity, tool_pool, tasks, _ = DEPARTMENT_SCENARIOS[row['avdeling']]
    role = row['stilling'].lower()
    if any(t in role for t in ('digital', 'innholdsprodusent', 'kommunikasjon', 'økonomi', 'administrasjon')):
        propensity = min(0.95, propensity + 0.15)
    if any(t in role for t in ('vekter', 'kafémedarbeider', 'butikkmedarbeider', 'montør')):
        propensity = max(0.1, propensity - 0.15)
    applicable = status != 'future' and end >= AI_START
    knowledge = 'not_applicable' if not applicable else rng.choices(
        ['synthetic_report', 'assumed', 'unknown'], weights=[65, 23, 12])[0]
    observed = min(end, REFERENCE_DATE) if applicable else None
    profile = {
        'person_id': pid, 'department': row['avdeling'], 'department_id': dept,
        'employment_status': status, 'observation_date': observed,
        'knowledge_status': knowledge, 'tools': [],
        'frequency': 'not_applicable' if not applicable else 'unknown',
        'competence': None, 'maturity': None, 'task_types': [],
        'description': '', 'source': SOURCE + '#ansatt_id=' + pid,
        'method': METHOD, 'synthetic': True,
        'period_start': max(start, AI_START) if applicable else None,
        'period_end': observed,
        'basis': ['avdeling:' + dept, 'stilling:' + row['stilling']],
        'uncertainty': 'Ikke en måling; konstruert scenario uten individuell dokumentasjon.',
    }
    if knowledge == 'not_applicable':
        profile['description'] = ('Fremtidig ansettelse; ingen nåværende KI-vurdering.' if status == 'future'
                                  else 'Ansettelsen sluttet før demoens moderne KI-periode; ingen bruk konstruert.')
    elif knowledge == 'unknown':
        profile['description'] = 'Syntetisk manglende svar. Verktøy, bruk og vurderinger er ukjent; dette betyr ikke aldri-bruk.'
    else:
        uses_ai = rng.random() < propensity
        profile['frequency'] = rng.choices(['daily', 'weekly', 'monthly'], [propensity, 0.8, 1 - propensity])[0] if uses_ai else 'never'
        if uses_ai:
            profile['tools'] = sorted(rng.sample(tool_pool, k=rng.randint(1, len(tool_pool))))
            profile['task_types'] = sorted(rng.sample(tasks, k=rng.randint(1, len(tasks))))
        # Kompetanse og modenhet er separate dimensjoner, også for aldri-brukere.
        profile['competence'] = rng.choices([1, 2, 3, 4, 5], [1, 2, 3, 2, 1] if uses_ai else [4, 3, 2, 1, 0.5])[0]
        profile['maturity'] = rng.choices([1, 2, 3, 4, 5], [1, 2, 3, 2, 1] if uses_ai else [5, 3, 1, 0.5, 0.2])[0]
        kind = 'Konstruert demosvar' if knowledge == 'synthetic_report' else 'Antakelse fra rolle-/oppgavemal'
        profile['description'] = kind + '. ' + ('Historisk periode; ikke nåværende bruk. ' if status == 'historical' else '')
        profile['description'] += ('Mulig KI-støtte i utvalgte oppgaver; innhold må kontrolleres.' if uses_ai
                                   else 'Ingen bruk i denne syntetiske perioden; dette er et eksplisitt demosvar.')
    return profile
