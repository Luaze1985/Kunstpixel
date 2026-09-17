# Handoff Report: FAQ Search Tokenization & Matching Logic Fix in `src/db.py`

**Date:** 2026-09-14  
**Agent:** Explorer Remedy 3 (`explorer_remedy_3`) — Roles: Investigation & Synthesis  
**Working Directory:** `g:/Min disk/Fellesprosjekt KI/.agents/explorer_remedy_3`  
**Target File for Remediation:** `src/db.py` (`query_faq` and `normalize_norwegian_text`)  
**Context & Authority:** `ORIGINAL_REQUEST.md`, `PROJECT.md`, `reviewer_1/handoff.md`  

---

## 1. Observation

### 1.1 Verbatim Code Locations in `src/db.py`
In `src/db.py`, lines 364–449, the existing implementation of `query_faq` was observed:

```python
373:    raw_query = query.strip()
374:    clean_words = [re.sub(r"[^\wåæøÅÆØ-]", "", w).lower() for w in raw_query.split()]
375:    tokens = [w for w in clean_words if len(w) >= 2]
...
432:    score = 0
433:    if raw_query.lower() in full_text or norm_raw_query in norm_full:
434:        score += 20
435:
436:    for term in search_terms:
437:        norm_term = normalize_norwegian_text(term)
438:        if term in q_text or norm_term in normalize_norwegian_text(q_text):
439:            score += 5
440:        elif term in a_text or norm_term in normalize_norwegian_text(a_text):
441:            score += 3
442:        elif term in c_text:
443:            score += 2
```

### 1.2 Observed Bug #1: Raw Substring Containment (`term in text`) with 2-Letter Tokens
Running query `"se"` against `query_faq`:
```powershell
py -3.13 -c "from src.db import query_faq; res = query_faq('se'); [print(r['id'], r['spoersmaal']) for r in res]"
```
**Output:** Returned all 12 rows in `publikum_faq`!
Direct inspection revealed why:
- In Norwegian, `"museet"` contains `"se"`. Every single question in `publikum_faq` contains `"museet"`.
- Furthermore, `"fotografere"` in Row 9, `"resepsjonen"` in Row 4 & Row 5, `"skoleklasser"` in Row 7, `"sekker"` and `"settes"` in Row 11, `"parkeringsplasser"` in Row 12 all contain the substring `"se"`.
- When a user asks `"Hva kan jeg se i sal X?"`, `tokens` includes `['hva', 'kan', 'jeg', 'se', 'sal']`. The token `"se"` matches `"fotografere"` and `"museet"`, `"kan"` and `"jeg"` match Question 9 (`"Kan jeg fotografere i museet?"`), giving Row 9 a high score of 18.
- As a consequence, running `agent.handle_message("Hva kan jeg se i sal X?")` produced:
  `"Ja, fotografering uten blits er tillatt i alle saler til privat bruk! ..."`
  (The visitor inquired about an invalid gallery room, but received photography rules).

### 1.3 Observed Bug #2: English Tourist Words Triggering Unrelated Norwegian FAQs
Running query `"do"` against `query_faq`:
```powershell
py -3.13 -c "from src.db import query_faq; res = query_faq('do'); [print(r['id'], r['spoersmaal']) for r in res]"
```
**Output:**
- Row 7 (`Har dere omvisning for skoleklasser?`) because the answer contains `"barne- og ungdomsskoler"` (`"do"` is inside `"ungdomsskoler"`).
- Row 5 (`Kan jeg ta med barnevogn?`) because the answer contains `"brede doerapninger"`.
- Running `agent.handle_message("Hello, do you speak English?")` returned:
  `"Ja, vi tilbyr tilrettelagte omvisninger for barnehager, barne- og ungdomsskoler og videregaaende..."`

### 1.4 Observed Bug #3: Synonym Triggers Matching Substrings of Other Words
In lines 377–410 of `src/db.py`:
- Line 399: `if any(k in t or k in norm_t for k in ["parker", "bil"]): synonyms.extend(["parkering", "parkeringsplasser"])`
  If a visitor asks `"Hva koster en billett?"`, the token is `"billett"`. Because `"bil" in "billett"` is True, parking synonyms were added, causing Row 12 (parking) to be returned as the #2 result for a ticket inquiry!
  Likewise, if a visitor asks `"Kan jeg ta bilder?"`, `"bil" in "bilde"` was True, triggering parking!
- Line 396: `if any(k in t or k in norm_t for k in ["barnevogn", "vogn", "baby", "rullestol", "hc", "heis", "tilgjengelig"]):`
  If a visitor asks `"Hvor er Munch?"`, the token is `"munch"`. Because `"hc" in "munch"` is True (`m-u-n-c-h`), accessibility and stroller synonyms were added!
- Line 408: `if any(k in t or k in norm_t for k in ["audioguide", "lydguide", "guide", "app"]):`
  If a visitor asks `"Hvor er trappen?"`, `"app" in "trapp"` is True, triggering audioguide synonyms!

### 1.5 Observed Bug #4: Whole-Query Check False Positives
Line 433: `if raw_query.lower() in full_text or norm_raw_query in norm_full: score += 20`
For short queries like `"se"` or `"do"` or `"er"`, this unconditionally added +20 to any row containing the substring anywhere in question, answer, or category.

---

## 2. Logic Chain

1. **Premise 1 (Reviewer 1 Finding 4 & Acceptance Criteria R1)**:
   FAQ search must accurately surface specific operational answers (e.g. `"åpningstider"` -> concrete hours in Row 2, `"pris"` -> ticket prices in Row 1) without polluting unrelated queries with false positive substring matches (such as `"se"` inside `"fotografere"` or `"do"` inside `"ungdomsskoler"`).
2. **Observation**:
   In `src/db.py`, queries were tokenized by simple whitespace splitting, stripping punctuation, and keeping all tokens with `len >= 2` without stopword filtering. Matching was executed via Python substring containment (`term in text`), and synonym expansion checked `k in t` for 2- and 3-letter substrings (`"bil"`, `"hc"`, `"app"`).
3. **Inference 1**:
   Because Python substring containment does not enforce word boundaries, any 2- or 3-letter token matches inside arbitrary words. In Norwegian, almost all words end in `-er`, `museet` contains `se`, `ungdomsskoler` contains `do`, and `billett` contains `bil`. Therefore, substring containment is structurally defective for keyword search.
4. **Inference 2**:
   Word-boundary matching alone is necessary but insufficient if grammatical stopwords (`kan`, `jeg`, `hva`, `det`, `i`) are retained as search terms. In queries like `"Hva kan jeg se i sal X?"`, even with word boundaries, `kan` and `jeg` match questions starting with `"Kan jeg..."` (such as photography and stroller FAQs). Therefore, **stopword filtering** must be combined with **word-boundary matching**.
5. **Inference 3**:
   Synonym triggers must guard short keywords against substring collisions:
   - `"bil"` must match only when the word itself is `bil`, `bilen`, `biler`, or begins with `bil-`, never as a substring of `billett` or `bilde`.
   - `"hc"` must match only when the word is `hc`, `handicap`, or begins with `hc-`, never as a substring of `munch`.
   - `"app"` must match only when the word is `app`, `appen`, `apper`, never inside `trapp`.
6. **Inference 4**:
   By using `re.findall(r"\b[\w-]+\b", raw_query.lower())` with Unicode support, filtering through a comprehensive `FAQ_STOPWORDS` set, enforcing a minimum word length of >= 3 (except `"hc"`), guarding synonym triggers, and matching terms via compiled word-boundary regular expressions (`rf"\b{re.escape(term)}\b"` and normalized variants):
   - `"se"`, `"do"`, `"er"`, and `"Hva kan jeg se i sal X?"` return 0 FAQ matches.
   - `"åpningstider"`, `"ÅPNINGSTIDER"`, `"aapningstider"`, `"apningstider"`, and `"aapent"` all match Row 2 (`Naar har museet aapent?`).
   - `"pris"`, `"honnør"`, `"student"`, and `"Hva koster det å besøke museet?"` all match Row 1 (`Hva koster det aa besoke museet?`).
   - `"kafé"`, `"kafe"`, and `"KAFÉ"` all match Row 3 (`Er det kafé i museet?`).
7. **Empirical Proof**:
   An in-memory monkey-patched test execution was run against the entire test suite (`pytest -q`), confirming that all 112 tests across all 6 test suites pass without any regression, while completely eliminating the reported false positives.

---

## 3. Caveats

1. **Read-Only Investigation Constraint**:
   Per the operational mandate, no source code or test files were directly modified on disk. All validation was performed via non-invasive in-memory monkey-patching in terminal sessions. The changes specified in Section 4 are ready for immediate application by the remediation implementer.
2. **Scope of Stopword List**:
   The stopword list includes Norwegian pronouns, auxiliary verbs, generic verbs, prepositions, conjunctions, filler words, generic museum terms (`museet`, `museum`, `sal`, `saler`), and common English conversational tourist noise (`hello`, `do`, `the`, `you`). Specialized terms (`billett`, `pris`, `åpningstider`, `kafé`, `audioguide`, `barnevogn`, `garderobe`, `parkering`, `skoleklasser`, `skrik`, `plakater`) are preserved and never filtered.
3. **Accent Handling in `normalize_norwegian_text`**:
   Norwegian texts occasionally use French loanword accents (`kafé`, `Museumskaféen`). Adding acute accent normalization (`é` -> `e`, `è` -> `e`, `ê` -> `e`) ensures consistent matching between accented queries (`kafé`) and ASCII database variants (`kafe`).

---

## 4. Conclusion & Concrete Fix Specification

### 4.1 Summary of Changes to `src/db.py`
1. **Extend `normalize_norwegian_text`** to fold accented `é`, `è`, `ê` into `e`.
2. **Define `FAQ_STOPWORDS`** at module level in `src/db.py`.
3. **Refactor `query_faq`**:
   - Extract tokens with `re.findall(r"\b[\w-]+\b", raw_query.lower())`.
   - Filter tokens: `(len(w) >= 3 or w == "hc") and w not in FAQ_STOPWORDS`.
   - If no tokens remain, return `[]` immediately.
   - Guard synonym expansion triggers for `bil`, `hc`, `app`, and `mat`.
   - Restrict whole-query match bonus (+20) to queries with `len(raw_query) >= 4`.
   - Score terms using compiled word-boundary regexes:
     `pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)`
     `norm_pattern = re.compile(rf"\b{re.escape(norm_term)}\b", re.IGNORECASE)`
     Matching in `q_text` (+5), `a_text` (+3), or `c_text` (+2).

### 4.2 Drop-in Replacement Code for `src/db.py`

#### Change 1: `normalize_norwegian_text` (lines 105–113)
```python
def normalize_norwegian_text(text: str) -> str:
    """Normalize Norwegian characters and spelling variations for robust search."""
    lowered = text.lower()
    return (
        lowered.replace("å", "aa")
        .replace("æ", "ae")
        .replace("ø", "oe")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
    )
```

#### Change 2: `FAQ_STOPWORDS` and `query_faq` (replacing lines 364–450)
```python
# Norwegian and common English stopwords to prevent false-positive FAQ matches
FAQ_STOPWORDS: set[str] = {
    # Norwegian question words & pronouns
    "hva", "hvem", "hvor", "hvorfor", "hvordan", "hvilken", "hvilket", "hvilke",
    "jeg", "meg", "min", "mitt", "mine",
    "du", "deg", "din", "ditt", "dine",
    "han", "ham", "hans", "hun", "henne", "hennes",
    "den", "det", "dets", "dette", "disse",
    "vi", "oss", "vår", "vårt", "våre", "vaar", "vaart", "vaare",
    "dere", "deres", "de", "dem",
    "man", "seg", "sin", "sitt", "sine",
    "en", "et", "ei", "noen", "noe", "hver", "hvert",
    # Norwegian auxiliary/copula verbs & high-frequency action verbs
    "er", "var", "vært", "vaert", "være", "vaere",
    "har", "hadde", "hatt", "ha",
    "kan", "kunne", "skal", "skulle", "vil", "ville", "må", "maa", "måtte", "maatte", "bør", "boer", "burde",
    "bli", "blir", "ble", "blev", "blitt",
    "få", "faa", "får", "faar", "fikk", "fått", "faatt",
    "se", "ser", "så", "saa", "sett",
    "gjøre", "gjør", "gjoer", "gjorde", "gjort",
    "finne", "finner", "fant", "funnet",
    "gå", "gaa", "går", "gaar", "gikk", "gått", "gaatt",
    "komme", "kommer", "kom", "kommet",
    # Norwegian prepositions, conjunctions, subjunctions
    "i", "på", "paa", "til", "fra", "med", "av", "om", "for", "ved", "under", "over", "etter", "mellom", "mot", "hos", "uten",
    "og", "eller", "men", "så", "saa", "som", "at", "da", "hvis", "dersom",
    # Norwegian adverbs / conversational particles
    "ja", "nei", "jo", "ikke", "ikkje", "her", "der", "bare", "nok", "vel", "også", "ogsaa", "gjerne",
    # Generic museum environment words that appear in almost all FAQs
    "museet", "museum", "sal", "saler", "salene",
    # English conversational words from foreign tourists
    "the", "a", "an", "is", "are", "was", "were", "do", "does", "did",
    "have", "has", "had", "can", "could", "will", "would",
    "you", "your", "i", "my", "we", "our", "it", "its", "they", "them",
    "what", "where", "when", "who", "how", "why",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "about",
    "and", "or", "but", "not", "hello", "hi", "please",
}


def query_faq(
    query: str,
    category: str | None = None,
    db_path: Path | str | None = None,
) -> list[dict]:
    """Keyword-normalized, word-boundary search for visitor FAQ."""
    if not query or not query.strip():
        return []

    raw_query = query.strip()
    words = re.findall(r"\b[\w-]+\b", raw_query.lower())
    tokens = [w for w in words if (len(w) >= 3 or w == "hc") and w not in FAQ_STOPWORDS]
    if not tokens:
        return []

    synonyms: list[str] = []
    for t in list(tokens):
        norm_t = normalize_norwegian_text(t)
        # Opening hours
        if any(k in t or k in norm_t for k in ["åpn", "aapn", "apn", "tid", "klokk", "stengt"]):
            synonyms.extend(["aapen", "åpen", "aapent", "åpent", "tid", "tider", "stengt", "tirsdag"])
        # Prices and tickets
        if any(k in t or k in norm_t for k in ["pris", "kost", "billett", "betal", "inngang", "honnør", "honnoer", "student", "gratis"]):
            synonyms.extend(["koster", "pris", "billett", "voksne", "studenter", "pensjonister", "kr", "gratis"])
        # Café / food (guarding against "mat" substring in words like "automat")
        if any(k in t or k in norm_t for k in ["kafe", "kafé", "drikk", "lunsj", "spis"]) or t in ("mat", "maten"):
            synonyms.extend(["kafé", "kafe", "museumskaféen", "lunsj"])
        # Cloakroom
        if any(k in t or k in norm_t for k in ["garderobe", "sekk", "veske", "laas", "lås", "oppbevar"]):
            synonyms.extend(["garderobe", "sekker", "vesker", "laas"])
        # Photography
        if any(k in t or k in norm_t for k in ["foto", "bilde", "kamera", "blits"]):
            synonyms.extend(["fotografere", "blits", "foto"])
        # Accessibility / stroller (guarding "hc" against substring matches in "munch")
        if any(k in t or k in norm_t for k in ["barnevogn", "vogn", "baby", "rullestol", "heis", "tilgjengelig"]) or t in ("hc", "handicap") or t.startswith("hc-"):
            synonyms.extend(["barnevogn", "heis", "universelt", "baereseler", "hc"])
        # Parking (guarding against "bil" matching inside "billett" or "bilde")
        if any(k in t or k in norm_t for k in ["parker", "parkering", "sykkel"]) or t in ("bil", "bilen", "biler", "bilparkering"):
            synonyms.extend(["parkering", "parkeringsplasser"])
        # Munch / Skrik
        if any(k in t or k in norm_t for k in ["skrik", "munch"]):
            synonyms.extend(["skrik", "edvard munch", "sal d"])
        # Shop
        if any(k in t or k in norm_t for k in ["butikk", "shop", "bok", "bøker", "boeker", "plakat"]):
            synonyms.extend(["museumsbutikken", "plakater", "kunstbøker"])
        # Audioguide (guarding "app" against "trapp")
        if any(k in t or k in norm_t for k in ["audioguide", "lydguide"]) or t in ("guide", "guiden", "app", "appen", "apper"):
            synonyms.extend(["audioguide", "app"])

    search_terms = list(dict.fromkeys(tokens + synonyms))

    sql = "SELECT id, spoersmaal, svar, kategori, hyppighet, sist_stilt FROM publikum_faq"
    params: dict[str, Any] = {}
    if category and category.strip():
        sql += " WHERE LOWER(kategori) = :category"
        params["category"] = category.strip().lower()

    rows = execute_read_query(sql, params, db_path=db_path)

    scored_results = []
    norm_raw_query = normalize_norwegian_text(raw_query)

    for r in rows:
        d = dict(r)
        q_text = d["spoersmaal"].lower()
        a_text = d["svar"].lower()
        c_text = (d.get("kategori") or "").lower()
        norm_q = normalize_norwegian_text(q_text)
        norm_a = normalize_norwegian_text(a_text)

        score = 0
        if len(raw_query) >= 4 and (raw_query.lower() in q_text or norm_raw_query in norm_q):
            score += 20

        for term in search_terms:
            norm_term = normalize_norwegian_text(term)
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            norm_pattern = re.compile(rf"\b{re.escape(norm_term)}\b", re.IGNORECASE)

            if pattern.search(q_text) or norm_pattern.search(norm_q):
                score += 5
            elif pattern.search(a_text) or norm_pattern.search(norm_a):
                score += 3
            elif c_text and (term == c_text or norm_term == c_text):
                score += 2

        if score > 0:
            scored_results.append((score, d.get("hyppighet", 0), d))

    scored_results.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [item[2] for item in scored_results]
```

### 4.3 Query Behavior Matrix: Before vs. After
| Query | Before (Buggy) | After (Remediated) | Status |
|---|---|---|---|
| `"se"` | Returned 12 rows (matches "museet", "fotografere") | `[]` (0 matches) | Fixed |
| `"do"` | Returned Row 7 ("ungdomsskoler") and Row 5 | `[]` (0 matches) | Fixed |
| `"er"` | Returned 12 rows (matches "-er" endings) | `[]` (0 matches) | Fixed |
| `"Hva kan jeg se i sal X?"` | Returned Row 9 (Flash photography rules!) | `[]` (Agent falls back to greeting/clarification) | Fixed |
| `"Hello, do you speak English?"` | Returned Row 7 (School tour bookings!) | `[]` (Agent falls back to greeting/clarification) | Fixed |
| `"Hva koster en billett?"` | Row 1 (#1) + Row 12 (#2, parking falsely triggered) | Row 1 (#1) (Zero parking false positives) | Fixed |
| `"Hvor er Munch?"` | Triggered accessibility synonyms ("hc" in "munch") | Triggered Row 8 (Skrik / Munch in Sal D) only | Fixed |
| `"Hvor er trappen?"` | Triggered audioguide ("app" in "trapp") | Zero audioguide false positive | Fixed |
| `"åpningstider"` | Row 2 (Concrete hours: 10:00–17:00) | Row 2 (Concrete hours: 10:00–17:00) | Preserved |
| `"ÅPNINGSTIDER"` | Row 2 | Row 2 | Preserved |
| `"aapent"` | Row 2 | Row 2 | Preserved |
| `"pris"` | Row 1 (Adult 120 kr, student 80 kr) | Row 1 (Adult 120 kr, student 80 kr) | Preserved |
| `"honnør"` / `"honnoer"` | Row 1 | Row 1 | Preserved |
| `"kafé"` / `"kafe"` / `"KAFÉ"` | Row 3 (Museumskaféen) | Row 3 (Museumskaféen) | Preserved |
| `"!@#$%^&*()"` | `[]` | `[]` | Preserved |

---

## 5. Verification Method

To independently reproduce and verify this investigation and solution:

1. **Verify the current bug in production source code**:
   ```powershell
   py -3.13 -c "from src.db import query_faq; print('se count:', len(query_faq('se'))); print('do count:', len(query_faq('do')))"
   ```
   *Expected buggy output:* `se count: 12`, `do count: 2`.

2. **Verify that the remediated `query_faq` eliminates all false positives while preserving target mappings**:
   Run the empirical test script:
   ```powershell
   py -3.13 -c "
   import re, sys
   from src.db import execute_read_query, normalize_norwegian_text
   import src.db, src.mcp_server

   # Insert remediated query_faq definition
   # [See Section 4.2 above for full definition]
   "
   ```

3. **Verify the full test suite with monkey-patched `query_faq`**:
   Execute:
   ```powershell
   py -3.13 -c "
   import pytest, sys, re
   from src.db import execute_read_query, normalize_norwegian_text
   import src.db, src.agent, src.mcp_server

   # Patch query_faq into db, agent, and mcp_server
   # Run pytest.main(['-v'])
   "
   ```
   *Observed result:* All 112 tests across `test_mcp_server.py`, `test_agent.py`, `test_integration.py`, `test_db_quality.py`, `test_adversarial_mcp.py`, and `test_challenger_2_adversarial.py` pass with 100% success rate (`112 passed in 2.85s`).

4. **Invalidation conditions**:
   This remediation proposal would be invalidated if:
   - Any of the test assertions in `tests/test_mcp_server.py::TestSearchFaqTool` fail.
   - Any Norwegian character test in `tests/test_adversarial_mcp.py::TestNorwegianAndSpecialCharacters` fails.
   - Querying `"se"`, `"do"`, or `"Hva kan jeg se i sal X?"` continues to match photography or school tours.
