# © 2026 Temporada Viral. Licença de uso pessoal do comprador; redistribuição proibida. Termos: https://temporadaviral.com/termos.html | Autoria: AUTORIA.md | TVK-2026-AF-CC02968C
"""`python -m prefs` (a partir de kit/): mostra o que o canal mudou do recomendado e os avisos."""
import sys

from prefs import avisos, carregar, faltando, para_ia

for fluxo in (sys.stdout, sys.stderr):
    try:
        fluxo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

print("Preferências do canal (o que mudou do recomendado):")
print(para_ia())
for a in avisos(carregar()):
    print("AVISO", a)
falta = faltando()
if falta:
    print("FALTA PREENCHER:", ", ".join(r for _, _, r in falta))
