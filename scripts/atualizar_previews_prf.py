from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'dashboard'
template=(p/'template.html').read_text(encoding='utf-8')
for name in ['preview_prf.html','preview_prf_externo.html','preview_prf_vazio.html']:
    existing=(p/name).read_text(encoding='utf-8')
    payload=re.search(r'<script type="application/json" class="ld-data">([\s\S]*?)</script>',existing).group(1)
    document='<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PRF · Segurança viária</title><style>html,body{margin:0;padding:0;background:#0b121b}</style></head><body>'+template.replace('__PRF_GOLD_PAYLOAD__',payload)+'</body></html>'
    (p/name).write_text(document,encoding='utf-8')
print('Previews atualizados; payloads recebidos do modelo preservados.')
