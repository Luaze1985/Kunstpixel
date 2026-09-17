# BRIEFING — 2026-09-14T15:45:00Z

## Mission
Investigate and design a clean, robust Norwegian keyword matching and word-boundary tokenization fix for `src/db.py` (`query_faq`) addressing substring false positives identified by Reviewer 1 while preserving 100% of test behavior across all suites.

## 🔒 My Identity
- Archetype: explorer
- Roles: [investigation, synthesis]
- Working directory: g:/Min disk/Fellesprosjekt KI/.agents/explorer_remedy_3
- Original parent: 7a113f74-d69a-4786-89b6-4115c75be748
- Milestone: Remediation Planning - FAQ Matching Fix

## 🔒 Key Constraints
- Read-only investigation — do NOT implement in source/tests directly
- Output strictly in `.agents/explorer_remedy_3/`
- Deliver findings and detailed fix strategy in `handoff.md`
- Send completion message to parent via `send_message`

## Current Parent
- Conversation ID: 7a113f74-d69a-4786-89b6-4115c75be748
- Updated: 2026-09-14T15:37:04Z

## Investigation State
- **Explored paths**:
  - `g:/Min disk/Fellesprosjekt KI/.agents/ORIGINAL_REQUEST.md`
  - `g:/Min disk/Fellesprosjekt KI/PROJECT.md`
  - `g:/Min disk/Fellesprosjekt KI/.agents/reviewer_1/handoff.md`
  - `src/db.py` (specifically `normalize_norwegian_text` lines 105–113, and `query_faq` lines 364–450)
  - `src/agent.py` (message routing, `_extract_room_query`, and fallback flow)
  - Database table `publikum_faq` (all 12 rows, 207 distinct vocabulary terms)
  - Pytest suites: `tests/test_mcp_server.py`, `tests/test_agent.py`, `tests/test_integration.py`, `tests/test_adversarial_mcp.py`, `tests/test_challenger_2_adversarial.py`, `tests/test_db_quality.py`
- **Key findings**:
  1. Root cause of `se`, `do`, `er` false positives: `src/db.py` used raw string containment (`term in text`) without word boundaries and allowed tokens of length >= 2 without stopword filtering.
  2. Substring containment caused "se" to match "museet" (present in nearly every FAQ), "fotografere", "resepsjonen", etc.
  3. "do" matched "ungdomsskoler" (FAQ 7) and "doerapninger" (FAQ 5).
  4. Synonym triggers contained dangerous substrings: `"bil"` in `["parker", "bil"]` falsely triggered parking on `"billett"` and `"bilde"`; `"hc"` matched inside `"munch"`; `"app"` matched inside `"trapp"`.
  5. Whole-query check (`raw_query.lower() in full_text`) gave +20 unconditionally on 2-letter queries matching "museet".
  6. Designed solution: Comprehensive `FAQ_STOPWORDS` list, `re.findall(r"\b[\w-]+\b", ...)`, token filtering `(len >= 3 or w == 'hc') and w not in FAQ_STOPWORDS`, strict word-boundary regex matching (`rf"\b{re.escape(term)}\b"` and normalized variant), guarded synonym expansion triggers, and acute accent normalization (`é` -> `e`).
  7. Verification: In-memory monkey-patch execution confirmed 100% pass rate (112/112 tests pass in pytest), and zero false positives on adversarial queries.
- **Unexplored areas**: None. Complete investigation and verified fix design achieved.

## Key Decisions Made
- Confirmed word-boundary regex `rf"\b{re.escape(term)}\b"` combined with `FAQ_STOPWORDS` and `len >= 3 or w == 'hc'` completely eliminates false positives while preserving opening hours ("åpningstider" -> Row 2) and prices ("pris" -> Row 1).
- Confirmed guarded synonym triggers for "bil", "hc", "app", and "mat".
- Confirmed accent folding in `normalize_norwegian_text` (`é` -> `e`).

## Artifact Index
- `g:/Min disk/Fellesprosjekt KI/.agents/explorer_remedy_3/DISPATCH.md` — logged incoming instructions
- `g:/Min disk/Fellesprosjekt KI/.agents/explorer_remedy_3/BRIEFING.md` — persistent agent memory & state
- `g:/Min disk/Fellesprosjekt KI/.agents/explorer_remedy_3/progress.md` — task completion tracker
- `g:/Min disk/Fellesprosjekt KI/.agents/explorer_remedy_3/handoff.md` — complete 5-component handoff report & fix specification
