from src.db import (
    query_collection,
    query_artwork_details,
    query_room_artworks,
    query_events,
    query_faq,
    get_db_connection,
)

# 1. Arbitrary search not in any test
res_backer = query_collection(artist="Backer")
print(f"Backer query returned {len(res_backer)} works: {[w['tittel'] for w in res_backer]}")

res_olje = query_collection(technique="Olje")
print(f"Olje technique query returned {len(res_olje)} works")

res_sal_c = query_room_artworks("SAL-C")
print(f"SAL-C query returned {len(res_sal_c)} works: {[w['tittel'] for w in res_sal_c]}")

res_mag = query_room_artworks("MAG-1")
print(f"MAG-1 query returned {len(res_mag)} works (exhibited filter)")

res_details = query_artwork_details("AURA-2026-005")
print(f"AURA-2026-005 details: {res_details['tittel']} by {res_details['kunstner']}, room: {res_details['sal_id']}")

res_faq = query_faq("garderobe")
print(f"FAQ garderobe query returned: {[f['spoersmaal'] for f in res_faq]}")

res_events = query_events(event_type="verksted")
print(f"Events verksted query returned: {[e['tittel'] for e in res_events]}")
