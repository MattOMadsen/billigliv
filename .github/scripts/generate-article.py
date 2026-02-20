import os
import xmltodict
import requests
from datetime import datetime
import re

today = datetime.now().strftime('%Y-%m-%d')
grok_key = os.getenv('GROK_API_KEY')

print("=== Starter BilligLiv auto-artikel generation ===")
print(f"Dato: {today}")

if not grok_key:
    print("FEJL: GROK_API_KEY secret mangler!")
    exit(1)

# Tjek XML-fil
xml_path = 'programs.xml'
if not os.path.exists(xml_path):
    print("FEJL: programs.xml findes ikke!")
    exit(1)

size = os.path.getsize(xml_path)
print(f"XML-fil størrelse: {size} bytes")

with open(xml_path, 'r', encoding='iso-8859-1') as f:
    raw = f.read()
    print("=== FØRSTE 1000 TEGN AF programs.xml ===")
    print(raw[:1000])
    print("=== SLUT PÅ DEBUG ===")

if size == 0 or not raw.strip():
    print("FEJL: XML-filen er tom!")
    exit(1)

if not raw.strip().startswith('<?xml') and not raw.strip().startswith('<'):
    print("FEJL: Dette er ikke XML – sandsynligvis fejlside fra Partner-Ads!")
    exit(1)

# Parse nu
try:
    data = xmltodict.parse(raw)['partnerprogrammer']['program']
    print(f"✅ Hentet {len(data) if isinstance(data, list) else 1} programmer")
except Exception as e:
    print("Parse-fejl:", str(e))
    exit(1)

# Resten af scriptet (Grok-kald, artikel-generering osv.)
system_prompt = """Du er BilligLivs AI-skribent. Skriv ALTID i naturlig, venlig Midtjylland-tone som om vi snakker over kaffen i Viborg..."""  # (samme som før)

# ... (resten af koden er uændret fra sidst – Grok-kald, gem fil osv.)

# (Hvis du vil have hele scriptet samlet, sig "send hele py" – men debug-delen er det vigtigste nu)

print("✅ Debug færdig – kører videre til Grok")
