from src.mcp_server import (
    search_collection,
    get_artwork_details,
    get_room_artworks,
    search_events,
    search_faq,
)

# Test mcp tools directly
# 1. Search by theme
res_theme = search_collection(theme="angst")
print(f"Theme angst: {len(res_theme)} works -> {[w['tittel'] for w in res_theme]}")

# 2. Search details for AURA-2026-016
res_16 = get_artwork_details("AURA-2026-016")
print(f"Artwork 16: {res_16['tittel']} by {res_16['kunstner']}, technique: {res_16['teknikk']}, room: {res_16['sal_id']}")

# 3. Get room artworks for SAL-B
res_b = get_room_artworks("SAL-B")
print(f"SAL-B artworks: {len(res_b)} works -> {[w['tittel'] for w in res_b]}")

# 4. Search faq for billett
res_faq = search_faq("billett")
print(f"FAQ billett: {len(res_faq)} results -> {[f['spoersmaal'] for f in res_faq]}")

# 5. Non-existent room
res_bad_room = get_room_artworks("SAL-Z")
print(f"Bad room result: {res_bad_room}")

# 6. Non-existent artwork
res_bad_art = get_artwork_details("AURA-9999-999")
print(f"Bad art result: {res_bad_art}")
