import os
import re

base_path = '/content/h5_bestilling'

# Ordbøker med unike, godkjente tekster tilpasset alle mulige TODO-felter i alle skjeletter.
# Ingen tall, kun godkjente roller (Museumsdirektør, Styret, Driftsansvarlig, Kafeansvarlig, Verneombud)

myndigheter_data = {
    "MK-01": {
        "hva_de_vil": "Tilsynet krever systematisk dokumentasjon på helse, miljø og sikkerhet samt referater fra vernerunder.",
        "utloser": "Periodiske kontroller eller innsendte bekymringsmeldinger fra ansatte angående arbeidsforhold.",
        "dokumentasjon": "Gjeldende risikovurderinger, avvikslogger og handlingsplaner for arbeidsmiljøet."
    },
    "MK-02": {
        "hva_de_vil": "Tilsynet krever trygg mathåndtering, renhold på kjøkkenet og sporbarhet på alle råvarer.",
        "utloser":