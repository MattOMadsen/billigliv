import os
import xmltodict
import requests
from datetime import datetime
import re

today = datetime.now().strftime('%Y-%m-%d')
grok_key = os.getenv('GROK_API_KEY')

# Hent og pars XML
with open('programs.xml', 'r', encoding='iso-8859-1') as f:
    data = xmltodict.parse(f.read())['partnerprogrammer']['program']

# Send til Grok for at vælge tema + 4-6 programmer + generere fuld artikel
system_prompt = """Du er BilligLivs AI-skribent. Skriv ALTID i naturlig, venlig Midtjylland-tone som om vi snakker over kaffen i Viborg. Brug "jeg har selv prøvet det i mit hus i Viborg", konkrete tal, Silkeborg/Viborg-eksempler, tabeller, 5 hacks, FAQ, konklusion. Ingen "godkendt til", ingen akavede sætninger. Brug shortcode {{< affiliate "key" "tekst" >}} hvis linket findes i yml. Ellers brug programnavn. Lav også Grok Imagine prompts til featured + 2 interne billeder (1600x900, WebP)."""

user_prompt = f"""Dato: {today}
Godkendte programmer: {str(data)[:8000]}  # begræns for token

Vælg ét stærkt emne (f.eks. forsikring, strøm, madplan, abonnementer, opsparing) med 4-6 programmer der passer sammen.
Generér FULD Hugo markdown artikel (1800-2500 ord) i præcis BilligLiv-stil.
Inkluder frontmatter med title, date, description, slug, cover image (brug emne-featured-...-2026.webp), tags, categories.
Tilføj 3 Grok Imagine prompts i bunden som kommentarer.
Output kun den rene markdown fil klar til content/emne/index.md"""

headers = {
    "Authorization": f"Bearer {grok_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "grok-2",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.7
}

response = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
article_md = response.json()['choices'][0]['message']['content']

# Find slug fra Grok-output eller lav en
slug = re.search(r'slug: "([^"]+)"', article_md) or "auto-artikel-" + today
filename = f"content/{slug}/index.md" if '/' in slug else f"content/{slug}/index.md"

os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, 'w', encoding='utf-8') as f:
    f.write(article_md)

# Ekstra: opdater affiliate_links.yml hvis nye links (simpel append)
# ... (kan udvides senere)

print(f"Artikel genereret: {filename}")
os.environ['TODAY'] = today
os.environ['TOPIC'] = slug.upper()
os.environ['SELECTED_PROGRAMS'] = "Se PR for detaljer"
