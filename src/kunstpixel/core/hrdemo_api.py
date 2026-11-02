"""Minimal localhost HTTP JSON API for the immutable Kunstpixel demo snapshot.

No authentication or TLS: do not expose this server on a public interface.
"""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from src.kunstpixel.core.hrdemo import (
    RUNTIME,
    candidates,
    count_skill,
    find_rules,
    get_person,
    list_people,
    list_skills,
    search_hms_guidance,
)
from src.kunstpixel.core.hr_eval import evaluate_staffing_proposal

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        def arg(key, default=None):
            vals = query.get(key)
            return vals[0] if vals else default
        try:
            if parsed.path == '/api/v1/health':
                result = {'service':'kunstpixel-hr-demo','status':'ok','db_path':str(RUNTIME)}
            elif parsed.path == '/api/v1/hr/skills':
                result = list_skills()
            elif parsed.path == '/api/v1/hr/skills/count':
                result = count_skill(arg('code','kasse'),arg('date','2026-11-07'))
            elif parsed.path == '/api/v1/hr/people':
                pid = arg('id')
                if pid:
                    res = get_person(pid, as_of=arg('date','2026-11-07'))
                    if res is None:
                        return self.respond(404, {'error': 'PERSON_NOT_FOUND', 'id': pid})
                    result = res
                else:
                    active_only = str(arg('active_only', 'false')).lower() in ('1', 'true', 'yes')
                    result = list_people(active_only=active_only)
            elif parsed.path == '/api/v1/hr/candidates':
                result = candidates(arg('date','2026-11-07'),arg('start','10:00'),
                                    arg('end','16:00'),int(arg('need','5')))
            elif parsed.path == '/api/v1/hr/evaluate':
                raw_ids = query.get('ids', query.get('id', []))
                suggested_ids = []
                for item in raw_ids:
                    suggested_ids.extend([x.strip() for x in item.split(',') if x.strip()])
                result = evaluate_staffing_proposal(
                    suggested_ids=suggested_ids,
                    work_date=arg('date', '2026-11-07'),
                    start=arg('start', '10:00'),
                    end=arg('end', '16:00'),
                    need=int(arg('need', '5')),
                )
            elif parsed.path == '/api/v1/hr/hms-guidance':
                result = search_hms_guidance(query=arg('q', None), topic=arg('topic', None), limit=int(arg('limit', '5')))
            elif parsed.path == '/api/v1/rules':
                result = find_rules(arg('domain',None),arg('topic',None),arg('date','2026-11-07'))
            else:
                return self.respond(404,{'error':'NOT_FOUND'})
            self.respond(200,result)
        except (ValueError,TypeError) as exc:
            self.respond(400,{'error':'INVALID_INPUT','detail':str(exc)})
        except FileNotFoundError:
            self.respond(503,{'error':'DEMO_NOT_INITIALIZED'})

    def respond(self,code,body):
        data=json.dumps(body,ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__=='__main__':
    print('Kunstpixel demo API: http://127.0.0.1:8765 (kun lokalt)')
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
