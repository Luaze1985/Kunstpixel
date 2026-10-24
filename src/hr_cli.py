"""Command line interface for Kunstpixel HR, HMS, and Quality read model.

Usage examples:
    py src/hr_cli.py init [--reset]
    py src/hr_cli.py kiosk [--date 2026-11-07] [--need 5]
    py src/hr_cli.py rules [--domain HMS] [--topic avvik]
    py src/hr_cli.py skills
    py src/hr_cli.py people [--active-only]
    py src/hr_cli.py person E101
    py src/hr_cli.py count kasse [--date 2026-11-07]
    py src/hr_cli.py eval E101,E102,E106,E103,E111
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kunstpixel.core.hrdemo import (
    RUNTIME,
    candidates,
    count_skill,
    find_rules,
    get_person,
    init_demo,
    list_people,
    list_skills,
    search_hms_guidance,
)
from src.kunstpixel.core.hr_eval import evaluate_staffing_proposal
from src.kunstpixel.cases import list_cases, get_case, evaluate_case_response


def main() -> int:
    parser = argparse.ArgumentParser(description="Kunstpixel HR/HMS/Kvalitet CLI")
    subparsers = parser.add_subparsers(dest="command", help="Kommandoer")

    # init
    p_init = subparsers.add_parser("init", help="Initialiser lokal kombinert runtime-database")
    p_init.add_argument("--reset", action="store_true", help="Nullstill og gjenopprett arbeidskopi")
    p_init.add_argument("--db", default=str(RUNTIME), help="Sti til mål-database")

    # kiosk
    p_kiosk = subparsers.add_parser("kiosk", help="Generer deterministisk bemanningskandidatliste for kiosk")
    p_kiosk.add_argument("--date", default="2026-11-07", help="Arbeidsdato (YYYY-MM-DD)")
    p_kiosk.add_argument("--start", default="10:00", help="Starttid (HH:MM)")
    p_kiosk.add_argument("--end", default="16:00", help="Sluttid (HH:MM)")
    p_kiosk.add_argument("--need", type=int, default=5, help="Antall ansatte som trengs")
    p_kiosk.add_argument("--db", default=str(RUNTIME), help="Database")

    # rules
    p_rules = subparsers.add_parser("rules", help="Søk i gjeldende HR/HMS/Kvalitet-regler")
    p_rules.add_argument("--domain", choices=["HR", "HMS", "KVALITET"], default=None, help="Fagområde")
    p_rules.add_argument("--topic", default=None, help="Emne eller stikkord")
    p_rules.add_argument("--date", default="2026-11-07", help="Gyldighetsdato")
    p_rules.add_argument("--db", default=str(RUNTIME), help="Database")

    # skills
    p_skills = subparsers.add_parser("skills", help="List alle definerte ferdigheter i kompetansekatalogen")
    p_skills.add_argument("--db", default=str(RUNTIME), help="Database")

    # people
    p_people = subparsers.add_parser("people", help="List alle ansatte")
    p_people.add_argument("--active-only", action="store_true", help="Kun aktive ansatte")
    p_people.add_argument("--db", default=str(RUNTIME), help="Database")

    # person
    p_person = subparsers.add_parser("person", help="Hent detaljert personkort med ferdigheter og vakter")
    p_person.add_argument("id", help="Ansatt-ID (f.eks. E101)")
    p_person.add_argument("--date", default="2026-11-07", help="Gyldighetsdato for kompetansebevis")
    p_person.add_argument("--db", default=str(RUNTIME), help="Database")

    # count
    p_count = subparsers.add_parser("count", help="Tell nøyaktig antall aktive ansatte med gyldig ferdighet")
    p_count.add_argument("skill", help="Ferdighetskode (f.eks. kasse, allergen)")
    p_count.add_argument("--date", default="2026-11-07", help="Gyldighetsdato")
    p_count.add_argument("--db", default=str(RUNTIME), help="Database")

    # eval
    p_eval = subparsers.add_parser("eval", help="Evaluer et bemanningsforslag mot deterministiske orakler og KI-feller")
    p_eval.add_argument("ids", help="Kommaseparert liste med ansatt-ID-er (f.eks. E101,E102,E106)")
    p_eval.add_argument("--date", default="2026-11-07", help="Dato")
    p_eval.add_argument("--need", type=int, default=5, help="Bemanningsbehov")
    p_eval.add_argument("--db", default=str(RUNTIME), help="Database")

    # hms
    p_hms = subparsers.add_parser("hms", help="Søk i 344 autoritative nasjonale HMS- og arbeidsmiljøveiledningspunkter")
    p_hms.add_argument("query", nargs="?", default=None, help="Søkeord (f.eks. ergonomi, vernerunde, løft)")
    p_hms.add_argument("--topic", default=None, help="Tema (f.eks. Lederansvar, Risikovurdering)")
    p_hms.add_argument("--limit", type=int, default=5, help="Maks antall treff (standard 5)")

    # cases
    p_cases = subparsers.add_parser("cases", help="List alle 14 HR- og KI-øvingscaser med museumsrelevans")
    p_cases.add_argument("--relevance", choices=["SVÆRT HØY", "HØY", "MIDDELS", "LAV"], default=None, help="Filtrer etter museumsrelevans")
    p_cases.add_argument("--sector", default=None, help="Filtrer etter opprinnelig sektor")

    # case
    p_case = subparsers.add_parser("case", help="Vis fullstendige detaljer for én case")
    p_case.add_argument("id", help="Case-ID (f.eks. CASE-013 eller HR-013)")

    # eval-case
    p_eval_case = subparsers.add_parser("eval-case", help="Evaluer en KI-respons mot casens sikkerhetssperrer og feller")
    p_eval_case.add_argument("id", help="Case-ID (f.eks. CASE-013)")
    p_eval_case.add_argument("--text", required=True, help="Respons-tekst som skal evalueres")
    p_eval_case.add_argument("--role", default="leder", help="Rollen til den som spør (f.eks. leder, hr, ansatt)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "init":
            target = init_demo(target=args.db, reset=args.reset)
            print(f"Demobase initialisert: {target}")
            return 0

        if args.command == "kiosk":
            data = candidates(work_date=args.date, start=args.start, end=args.end, need=args.need, db_path=args.db)
        elif args.command == "rules":
            data = find_rules(domain=args.domain, topic=args.topic, as_of=args.date, db_path=args.db)
        elif args.command == "skills":
            data = list_skills(db_path=args.db)
        elif args.command == "people":
            data = list_people(active_only=args.active_only, db_path=args.db)
        elif args.command == "person":
            res = get_person(person_id=args.id, as_of=args.date, db_path=args.db)
            if res is None:
                print(f"Feil: Fant ingen ansatt med ID '{args.id}'.", file=sys.stderr)
                return 1
            data = res
        elif args.command == "count":
            data = count_skill(code=args.skill, as_of=args.date, db_path=args.db)
        elif args.command == "eval":
            raw_ids = [x.strip() for x in args.ids.split(",") if x.strip()]
            data = evaluate_staffing_proposal(suggested_ids=raw_ids, work_date=args.date, need=args.need, db_path=args.db)
        elif args.command == "hms":
            data = search_hms_guidance(query=args.query, topic=args.topic, limit=args.limit)
        elif args.command == "cases":
            cases = list_cases(museum_relevance=args.relevance, sector=args.sector)
            data = [
                {
                    "case_id": c.case_id,
                    "legacy_id": c.legacy_id,
                    "title": c.title,
                    "museum_relevance": c.museum_relevance,
                    "theme": c.theme,
                    "sector": c.sector,
                    "sop_ref": c.sop_ref,
                }
                for c in cases
            ]
        elif args.command == "case":
            c = get_case(args.id)
            if not c:
                print(f"Feil: Fant ikke case '{args.id}'.", file=sys.stderr)
                return 1
            data = {
                "case_id": c.case_id,
                "legacy_id": c.legacy_id,
                "title": c.title,
                "museum_relevance": c.museum_relevance,
                "sector": c.sector,
                "theme": c.theme,
                "brief": c.brief,
                "red_team_trap": c.red_team_trap,
                "expected_safe_response": c.expected_safe_response,
                "pass_criteria": c.pass_criteria,
                "sop_ref": c.sop_ref,
                "handbok_ref": c.handbok_ref,
                "ap9_questions": c.ap9_questions,
                "ap9_rules": c.ap9_rules,
                "conversation_refs": c.conversation_refs,
                "documents": [
                    {
                        "document_id": d.document_id,
                        "doc_type": d.doc_type,
                        "data_class": d.data_class,
                        "allowed_roles": d.allowed_roles,
                        "untrusted_source": d.untrusted_source,
                    }
                    for d in c.documents
                ]
            }
        elif args.command == "eval-case":
            res = evaluate_case_response(
                case_identifier=args.id,
                response_text=args.text,
                caller_role=args.role
            )
            data = res.to_dict()
        else:
            parser.print_help()
            return 1

        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    except Exception as e:
        print(f"Feil ved utførelse av '{args.command}': {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
