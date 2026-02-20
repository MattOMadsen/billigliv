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
    print("FEJL: GROK_API_KEY secret mangler! Tjek Settings → Secrets → Actions.")
    exit(1)

# Hent XML
with open('programs.xml', 'r', encoding='iso-8859-1') as f:
    data = xmltodict.parse(f.read())['partnerprogrammer']['program']

print(f"✅ Hentet {len(data)} programmer fra Partner-Ads")

system_prompt = """Du er BilligLivs AI-skribent. Skriv ALTID i naturlig, venlig Midtjylland-tone som om vi snakker over kaffen i Viborg. Brug "jeg har selv prøvet det i mit hus i Viborg", konkrete tal, Silkeborg/Viborg-eksempler, tabeller, 5 hacks, FAQ, konklusion. Ingen "godkendt til". Brug shortcode {{< affiliate "key" "tekst" >}} hvis linket findes i yml. Lav også 3 Grok Imagine prompts til billeder (1600x900 WebP)."""

user_prompt = f"""Dato: {today}
Godkendte programmer: {str(data)[:10000]}

Vælg ét stærkt emne med 4-6 programmer der passer sammen.
Generér FULD Hugo markdown artikel (1800-2500 ord) i præcis BilligLiv-stil.
Inkluder frontmatter med title, date, description, slug, cover image (emne-featured-...-2026.webp), tags, categories.
Tilføj 3 Grok Imagine prompts i bunden som kommentarer.
Output kun den rene markdown klar til content/emne/index.md"""

headers = {
    "Authorization": f"Bearer {grok_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "grok-4-latest",   # <-- nu med -latest som din curl
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.7
}

response = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
result = response.json()

if 'error' in result:
    print("Grok-fejl:", result['error'])
    exit(1)

article_md = result['choices'][0]['message']['content']

# Find slug og gem
slug_match = re.search(r'slug:\s*"([^"]+)"', article_md)
slug = slug_match.group(1) if slug_match else f"auto-{today}"
filename = f"content/{slug}/index.md"

os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, 'w', encoding='utf-8') as f:
    f.write(article_md)

print(f"✅ Artikel genereret og gemt som {filename}")
print(f"Emne: {slug}")

os.environ['TODAY'] = today
os.environ['TOPIC'] = slug.upper()
os.environ['SELECTED_PROGRAMS'] = "Se PR for detaljer"
