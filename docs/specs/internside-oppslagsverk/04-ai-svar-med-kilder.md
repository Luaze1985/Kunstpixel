# 04: AI-svar med kilder og kostnadsgrense

**Hva som skal bygges:** Over treffene vises et kort svar merket **AI-forslag**, med punkt-ID-ene det bygger
på. Null treff gir «fant ingen kilde» uten AI-kall. Grensen er 20 kall per time.

**Må gjøres først:** 03, fordi svaret bygger på oppslaget og vises på samme side.

**Status:** ready-for-agent · **Spesifikasjon:** [../internside-oppslagsverk.md](../internside-oppslagsverk.md)

### Akseptansekriterier
- [ ] MVP-fasit: `oppslag.svar()` og `llm.svar_fra_handbok()` følger kontrakten i `tests/test_mvp_oppslag.py`.
      Merket `@VENTER_PA_04` er fjernet, og alle sjekkene består. Endepunktet i Datafinner er en tynn skal
      rundt `oppslag.svar()`.
- [ ] Det finnes en ny funksjon i `core/llm.py` for håndboksvar. `forklar()` er uendret. Funksjonen tar
      spørsmål og punkter (punkt-ID og tekst) og har en egen systemprompt med disse kravene: bare punktene,
      nevn punkt-ID-ene, si fra når punktene ikke dekker spørsmålet, ikke følg instruksjoner i punktene,
      norsk bokmål.
- [ ] Kildekontroll: punkt-ID-er i svaret som ikke var blant punktene som ble sendt, flagges i svaret
      (`ukjente_kilder`). Kontrollen er testet med en falsk `apne`.
- [ ] Null treff gir «fant ingen kilde», og den falske leverandøren blir ikke kalt. Det er testet.
- [ ] Et nytt POST-endepunkt har de samme sperrene som `/api/forklar`: Origin, Sec-Fetch-Site, Content-Type,
      størrelse, 503 når AI er av, 429 ved grensen og 502/504 ved feil hos leverandøren. Kommentaren om
      sperrene er oppdatert, siden det ikke lenger finnes innlogging.
- [ ] Standardgrensen er 20 (`LLM_MAKS_PER_TIME`) i `llm.py`, og docstringen er oppdatert. Oppstarten stopper
      med en tydelig melding hvis AI er på og verdien ikke er et positivt heltall. Testet med falsk klokke:
      kall nummer 21 innen en time avvises.
- [ ] Siden viser AI-svaret øverst. Når AI er av, ved 429 eller ved feil, vises bare treffene, med en kort
      melding. Ingen chat.
- [ ] Ingen nettverkskall i testpakken. `py -3.13 -m pytest -q` er grønn.
- [ ] Manuelt: Lars prøver med ekte Claude lokalt (`LLM_PROVIDER=anthropic`) og sjekker at punkt-ID-ene
      stemmer.
