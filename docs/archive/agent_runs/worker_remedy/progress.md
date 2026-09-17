# Progress: Worker Remedy
Last visited: 2026-09-14T17:55:00+02:00
Status: Completed

- [x] Read ORIGINAL_REQUEST.md, PROJECT.md, TEST_READY.md, reviewer_1 handoff, and explorer_remedy reports (1, 2, 3)
- [x] Refactored src/db.py: Added accent folding, FAQ_STOPWORDS, and word-boundary regex matching in query_faq
- [x] Verified query_faq eliminates false positives for 'se', 'do', 'er', 'Hva kan jeg se i sal X?', 'Hello, do you speak English?'
- [x] Refactored src/agent.py:
  - Connected FastMCP tools from src.mcp_server via InProcessMCPClient
  - Implemented authentic per-turn tool execution tracking via _call_tool and self._turn_tools_used
  - Dynamically extracted pricing from search_faq in _handle_pricing
  - Dynamically extracted 30-min highlights from get_room_artworks in _handle_recommendation_30min with honest tools_used=['get_room_artworks']
  - Dynamically formatted FAQ responses from database svar in _handle_faq_result
  - Dynamically formatted events and children workshops from search_events in _handle_events
- [x] Verified complete test suite: All 112 tests pass (100%)
- [x] Verified database mutation reactivity: Modifying ticket prices dynamically reflected in agent output
- [x] Updated README.md
- [x] Written handoff.md
