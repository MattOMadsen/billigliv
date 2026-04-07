import os
import xmltodict
import requests
from datetime import datetime
from openai import OpenAI
import re

today = datetime.now().strftime('%Y-%m-%d')
grok_key = os.getenv('GROK_API_KEY')

client = OpenAI(base_url="https://api.x.ai/v1", api_key=grok_key)

print("=== BilligLiv Auto-Artikel v3.2 ===")
print(f"Dato: {today}")

# XML parse (fra workflow)
with open('programs.xml', 'r', encoding='iso-8859-1') as f:
    data = xmltodict.parse(f.read())['partnerprogrammer']['program']

programs = data if isinstance(data, list) else [data]
print(f"Programmer: {len(programs)}")

# Vælg top 3
top_programs = programs[:3]
topics = [p['navn'] for p in top_programs]

system_prompt = """
Du er BilligLivs AI-skribent. Skriv på naturligt dansk som nabo fra Viborg.

Struktur:
- Titel
- Intro med personlig historie
- Hvor meget sparer?
- Trin-for-trin
- Tabel
- 5-7 hacks
- FAQ
- Konklusion + CTA

Brug affiliate shortcodes: {{< affiliate \"key\" \"tekst\" >}}
Ingen salg, humor ok.
"""

for topic in topics:
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Skriv artikel om {topic} 2026."}]
    )
    article = response.choices[0].message.content

    # Gem
    filename = f"content/{topic.lower().replace(' ', '-')}/index.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.write(f"---\ntitle: \"{topic} 2026\"\ndate: {today}\n---\n\n{article}")

    # Billede prompt
    image_prompt = f"Viborg hus {topic} besparelse 2026, realistisk foto"
    # (Grok Imagine call – udvid senere)

print("Artikler genereret – PR klar!")

