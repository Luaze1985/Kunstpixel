# Risikoregister (Risks)

| ID | Risiko | Alvorlighet | Sannsynlighet | Tiltak / Reduksjon |
| :--- | :--- | :--- | :--- | :--- |
| **RSK-001** | **Faglige hallusinasjoner:** Agenter finner på årstall, kunstnerbiografier eller feiltolker verk. | Høy | Middels | All verksinformasjon må hentes fra validert database via MCP. Faktapåstander uten kilde merkes som hypotese. |
| **RSK-002** | **Overkomplisering av byråkrati:** Prosjektet drukner i simulert saksbehandling og forvaltningsrutiner i stedet for praktisk kode. | Høy | Lav (styrt) | Håndheve ADR-0001 strengt: Lean SMB-modell med fokus på plugins, MCP og undervisning. |
| **RSK-003** | **Uautorisert ekstern handling:** En agent sender e-post eller publiserer uferdig innhold til eksterne kanaler. | Svært høy | Lav | Strikt Nivå 3-godkjenningsport. Agenter har ikke skrivetilgang til eksterne API-er uten eier-token/godkjenning. |
| **RSK-004** | **Context rot / token-overforbruk:** For store kontekstfiler overbelaster agentens kontekstvindu. | Middels | Middels | Modulær kontekstarkitektur: Kun stabil kjerne (`context/core/`) lastes som standard. Prosjekt- og rollefiler lastes ved behov. |
