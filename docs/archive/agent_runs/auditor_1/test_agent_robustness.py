from src.agent import MuseumsvertAgent

agent = MuseumsvertAgent()

queries = [
    "Hvor finner jeg Christian Krohg sine verker?",
    "Hva handler Albertine om?",
    "Hvilke verker er utstilt i Sal C?",
    "Hvem har malt Blått interiør?",
    "Har museet noen verker av Nikolai Astrup?",
    "Fortell om Erik Werenskiold",
    "Hva koster et familiepass?",
    "Hva slags arrangementer har dere for voksne?",
    "Hva er åpningstidene på en søndag?",
    "Er det lov å ta bilder med blits?",
]

for q in queries:
    resp = agent.handle_message(q)
    print(f"\nQ: {q}")
    print(f"Cat: {resp.category} | Tools: {resp.tools_used} | Rooms: {resp.rooms_referenced}")
    print(f"Text snippet: {resp.text[:120]}...")
